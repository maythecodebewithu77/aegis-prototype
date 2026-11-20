"""
ADAPT Agent — "MonsoonRoute"
Checks a shipment's assigned route against live disruption events (flood,
closure, congestion) and, when the delay threatens the shipment's
perishability window, proposes a known alternate route.
"""
from .llm import explain


def check_route(shipment: dict, routes_data: dict) -> dict:
    route_id = shipment["route_id"]
    route = next((r for r in routes_data["routes"] if r["route_id"] == route_id), None)
    event = next((e for e in routes_data["disruption_events"] if e["route_id"] == route_id), None)

    if not event:
        return {
            "shipment_id": shipment["shipment_id"],
            "status": "ON_TRACK",
            "route": route,
            "disruption": None,
            "proposed_action": None,
            "requires_human_approval": False,
        }

    projected_eta = shipment["eta_hours"] + event["delay_hours"]
    perishability = shipment.get("perishability_hours")
    spoilage_risk = perishability is not None and projected_eta > perishability

    proposed_action = None
    if spoilage_risk or event["severity"] == "high":
        alt_ids = routes_data.get("alternates", {}).get(route_id, [])
        if alt_ids:
            alt_route = next((r for r in routes_data["routes"] if r["route_id"] == alt_ids[0]), None)
            proposed_action = {
                "type": "REROUTE",
                "from_route": route_id,
                "to_route": alt_route["route_id"] if alt_route else None,
                "new_path": alt_route["path"] if alt_route else None,
                "new_eta_hours": alt_route["normal_hours"] if alt_route else None,
            }

    return {
        "shipment_id": shipment["shipment_id"],
        "status": "AT_RISK" if spoilage_risk else "DELAYED",
        "route": route,
        "disruption": event,
        "projected_eta_hours": projected_eta,
        "spoilage_risk": spoilage_risk,
        "proposed_action": proposed_action,
        "requires_human_approval": proposed_action is not None,
    }


def run(shipment: dict, routes_data: dict, use_llm: bool = False) -> dict:
    result = check_route(shipment, routes_data)
    if result["disruption"]:
        prompt = (
            f"In two plain sentences, explain to a logistics officer what happened to "
            f"shipment {shipment['shipment_id']} ({shipment['description']}) and what "
            f"AEGIS is proposing to do about it. Details: {result}"
        )
        result["agent_explanation"] = explain(prompt, use_llm=use_llm) or (
            f"{result['disruption']['type'].replace('_', ' ').title()} on {result['disruption']['segment']} "
            f"adds {result['disruption']['delay_hours']}h to this shipment"
            + (", risking spoilage before arrival. " if result.get("spoilage_risk") else ". ")
            + (
                f"Proposing reroute via {result['proposed_action']['new_path']}."
                if result["proposed_action"]
                else "No safe alternate route is currently available — flagging for manual handling."
            )
        )
    else:
        result["agent_explanation"] = "No active disruption on this shipment's route. On track."
    return result
