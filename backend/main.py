"""
AEGIS backend — orchestrates SENSE, ADAPT, and RECOVER agents behind a
small REST API, with a shared audit log and a human-approval gate for any
action an agent proposes.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open ../frontend/index.html in a browser (it talks to localhost:8000).
"""
import json
import os
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import sense, adapt, recover

DATA_DIR = Path(__file__).parent / "data"
AUDIT_LOG_PATH = Path(__file__).parent / "audit_log.json"

app = FastAPI(title="AEGIS Prototype API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def _load_audit_log() -> list[dict]:
    if not AUDIT_LOG_PATH.exists():
        return []
    with open(AUDIT_LOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _append_audit(entry: dict):
    log = _load_audit_log()
    entry["log_id"] = str(uuid.uuid4())[:8]
    entry["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    log.insert(0, entry)  # newest first
    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    return entry


# In-memory store of the latest proposed action per shipment/component,
# so an /approve call knows exactly what it's approving.
_pending_actions: dict[str, dict] = {}


@app.get("/api/shipments")
def get_shipments():
    return _load("shipments.json")


@app.get("/api/sense/{component_id}")
def run_sense(component_id: str, use_llm: bool = False):
    suppliers_data = _load("suppliers.json")
    component = next((c for c in suppliers_data["components"] if c["component_id"] == component_id), None)
    if not component:
        raise HTTPException(404, f"Unknown component_id {component_id}")
    result = sense.run(component, suppliers_data["disruption_signals"], use_llm=use_llm)
    return result


@app.get("/api/adapt/{shipment_id}")
def run_adapt(shipment_id: str, use_llm: bool = False):
    shipments = _load("shipments.json")
    shipment = next((s for s in shipments if s["shipment_id"] == shipment_id), None)
    if not shipment:
        raise HTTPException(404, f"Unknown shipment_id {shipment_id}")
    routes_data = _load("routes.json")
    result = adapt.run(shipment, routes_data, use_llm=use_llm)
    if result.get("proposed_action"):
        key = f"adapt:{shipment_id}"
        _pending_actions[key] = {
            "pillar": "ADAPT",
            "subject": shipment_id,
            "description": f"Reroute {shipment_id} from {result['proposed_action']['from_route']} to {result['proposed_action']['to_route']}",
            "detail": result,
        }
    return result


@app.get("/api/recover/{component_id}")
def run_recover(component_id: str, use_llm: bool = False):
    suppliers_data = _load("suppliers.json")
    component = next((c for c in suppliers_data["components"] if c["component_id"] == component_id), None)
    if not component:
        raise HTTPException(404, f"Unknown component_id {component_id}")
    inventory = _load("recovery_inventory.json")
    result = recover.run(component_id, component["name"], inventory, use_llm=use_llm)
    if result.get("recommended_match"):
        key = f"recover:{component_id}"
        _pending_actions[key] = {
            "pillar": "RECOVER",
            "subject": component_id,
            "description": f"Source {result['recommended_match']['quantity']} recovered units from {result['recommended_match']['source']}",
            "detail": result,
        }
    return result


class ApprovalRequest(BaseModel):
    action_key: str  # e.g. "adapt:SHP-2001" or "recover:COMP-CHIP-07"
    decision: str    # "approved" or "rejected"
    approver_name: Optional[str] = "Demo Officer"
    note: Optional[str] = ""


@app.post("/api/approve")
def approve_action(req: ApprovalRequest):
    pending = _pending_actions.get(req.action_key)
    if not pending:
        raise HTTPException(404, f"No pending action found for key {req.action_key}")
    if req.decision not in ("approved", "rejected"):
        raise HTTPException(400, "decision must be 'approved' or 'rejected'")

    entry = _append_audit({
        "pillar": pending["pillar"],
        "subject": pending["subject"],
        "description": pending["description"],
        "decision": req.decision,
        "approver_name": req.approver_name,
        "note": req.note,
    })
    if req.decision == "approved":
        _pending_actions.pop(req.action_key, None)
    return entry


@app.get("/api/audit")
def get_audit_log():
    return _load_audit_log()


@app.get("/api/health")
def health():
    return {"status": "ok", "pillars": ["SENSE", "ADAPT", "RECOVER"]}
