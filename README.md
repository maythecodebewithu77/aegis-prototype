# AEGIS 🛡️
### Autonomous Ecosystem for Guarding Industrial Supply Chains

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/ASGI-Uvicorn-20B2AA.svg)](https://www.uvicorn.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Explainable%20Tri--Agent-orange.svg)](#core-architecture--the-three-pillars)
[![Governance](https://img.shields.io/badge/Governance-Human--in--the--Loop-purple.svg)](#human-in-the-loop-governance--audit-trail)
[![Team](https://img.shields.io/badge/Team-Nexus%20Polaris%20(HS26--112)-navy.svg)](#team--hackathon-context)

---

## 📌 Executive Summary

Modern industrial supply chains suffer from severe blind spots: **opaque multi-tier supplier dependencies**, **unanticipated transit route disruptions**, and **fragmented reverse-logistics recovery**. When disruptions strike, supply officers often lack actionable, explainable intelligence to avert line shutdowns or cargo spoilage.

**AEGIS** (*Autonomous Ecosystem for Guarding Industrial Supply chains*) is an agentic, explainable decision-support platform designed for industrial and agricultural logistics. It orchestrates three specialized autonomous agents (**SENSE**, **ADAPT**, and **RECOVER**) coupled with an auditable **Human-in-the-Loop (HITL)** approval gate and a zero-dependency real-time operational dashboard.

```
                      ┌─────────────────────────────────────────┐
                      │          OPERATOR DASHBOARD             │
                      │     (Real-Time Shipment Monitor)        │
                      └────────────────────┬────────────────────┘
                                           │ HTTP / REST
                      ┌────────────────────▼────────────────────┐
                      │            AEGIS CORE API               │
                      │               (FastAPI)                 │
                      └────┬───────────────┼───────────────┬────┘
                           │               │               │
            ┌──────────────▼─────┐  ┌──────▼──────┐  ┌─────▼──────────────┐
            │       SENSE        │  │    ADAPT    │  │      RECOVER       │
            │  "GhostSupplier"   │  │"MonsoonRoute"│ │    "ScrapLoop"     │
            │  Hidden Tier-2 Risk│  │Perishability│  │ Circular Sourcing  │
            │  Concentration &   │  │& Disruption │  │ Reverse-Logistics  │
            │  Signal Analysis   │  │  Rerouting  │  │ Condition Ranking  │
            └──────────────┬─────┘  └──────┬──────┘  └─────┬──────────────┘
                           │               │               │
                           └───────────────┼───────────────┘
                                           │
                      ┌────────────────────▼────────────────────┐
                      │      PLUGGABLE REASONING LAYER          │
                      │  (Claude Sonnet / SAP GenAI Hub / Local)│
                      └────────────────────┬────────────────────┘
                                           │
                      ┌────────────────────▼────────────────────┐
                      │     HUMAN-IN-THE-LOOP APPROVAL GATE     │
                      │    (Timestamped Audit Trail Logging)    │
                      └─────────────────────────────────────────┘
```

---

## 🧠 Core Architecture — The Three Pillars

AEGIS breaks supply chain resilience into three distinct, specialized pillars:

### 1. SENSE Agent — *"GhostSupplier"* (`backend/agents/sense.py`)
- **Mission**: Illuminates hidden dependencies beyond Tier-1 suppliers down to Tier-2 and Tier-3 vendors.
- **Mechanism**: Analyzes supply concentration percentages across sub-suppliers and correlates them with real-time external disruption signals (e.g., port congestion, factory shutdowns).
- **Output**: Generates a deterministic, explainable concentration risk score (0–100) and severity band (`LOW`, `MEDIUM`, `HIGH`).

### 2. ADAPT Agent — *"MonsoonRoute"* (`backend/agents/adapt.py`)
- **Mission**: Mitigates active transit disruptions while safeguarding perishable cargo.
- **Mechanism**: Evaluates active route segments against disruption events (e.g., flash flooding, highway blockades) and assesses whether projected delays exceed the cargo's strict perishability window.
- **Output**: Computes viable bypass routes (e.g., highway bypasses) and packages an actionable rerouting proposal for operational review.

### 3. RECOVER Agent — *"ScrapLoop"* (`backend/agents/recover.py`)
- **Mission**: Closes the loop through circular economy and reverse-logistics inventory substitution.
- **Mechanism**: In the event of primary component shortages, scans certified secondary inventory, ranking options based on quality condition (`Grade A`, `Grade B`) and geographic distance (km).
- **Output**: Generates emergency sourcing recommendations from nearest qualified recovery hubs.

---

## 🛡️ Key Innovations & Design Principles

- **Explainable & Deterministic By Design**: Every agent calculation is rule-based and auditable. Unlike unpredictable black-box models, AEGIS provides clear mathematical reasoning that judges, auditors, and supply chain executives can verify.
- **Pluggable Agentic LLM Layer (`backend/agents/llm.py`)**: Structured findings can be synthesized into natural-language briefs using Anthropic Claude (`claude-sonnet-4-6`) or **SAP Generative AI Hub**. Built-in template fallbacks guarantee flawless demo execution even without internet access.
- **Strict Human-in-the-Loop (HITL) Governance**: Autonomous agents can propose critical actions (e.g., rerouting cargo, procuring alternative stock), but cannot execute them without human sign-off. Every approval/rejection is tracked in an immutable audit ledger (`audit_log.json`).
- **Zero-Build Lightweight Frontend**: Pure vanilla HTML5/CSS/JavaScript with zero build tools (`node_modules` or bundlers) required.

---

## 📂 Repository Structure

```text
aegis-prototype/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── sense.py             # SENSE agent (Tier-2 supplier risk)
│   │   ├── adapt.py             # ADAPT agent (Perishability & rerouting)
│   │   ├── recover.py           # RECOVER agent (Reverse-logistics recovery)
│   │   └── llm.py               # Pluggable reasoning layer (Claude / SAP Hub)
│   ├── data/
│   │   ├── shipments.json       # Mock active shipment catalog
│   │   ├── suppliers.json       # Multi-tier supplier graph & disruption signals
│   │   ├── routes.json          # Route topologies, disruption events & alternates
│   │   └── recovery_inventory.json # Circular economy certified stock
│   ├── audit_log.json           # Real-time ledger of human approvals/rejections
│   ├── main.py                  # FastAPI application & REST endpoints
│   └── requirements.txt         # Backend Python dependencies
├── frontend/
│   └── index.html               # Single-page operations dashboard
├── .gitignore                   # Git exclusion rules
└── README.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12 installed
- **Modern Web Browser**: Chrome, Edge, Firefox, or Safari
- **Git**: Installed and configured

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/aegis-prototype.git
cd aegis-prototype
```

### Step 2: Set Up Python Backend
```bash
# Navigate to backend directory
cd backend

# Create and activate a virtual environment
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```
The backend API is now running at `http://127.0.0.1:8000`. You can explore the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### Step 4: Open the Frontend Dashboard
Simply open `frontend/index.html` in your web browser:
- **Windows**: Double-click `frontend/index.html` in File Explorer or run:
  ```powershell
  Start-Process frontend/index.html
  ```
- **macOS**: `open frontend/index.html`
- **Linux**: `xdg-open frontend/index.html`

*The frontend connects automatically to `http://127.0.0.1:8000` with no build steps or bundlers needed.*

---

## 🎬 Interactive Demo Walkthrough

Try this 3-step walkthrough to experience the full tri-agent loop:

| Step | Shipment ID | Scenario | Agent Triggered | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **`SHP-2001`** | **Perishable Mango Consignment** (Krishnagiri → Chennai Port) | **ADAPT** | High-severity flood detected on NH-44 (+30h delay vs 36h perishability). Status changes to **`AT_RISK`**. Agent proposes bypass route via `SH-9 (bypass)`. Click **Approve Reroute** to record the decision. |
| **2** | **`SHP-1001`** | **EV Battery Restock** (Shenzhen → Chennai) | **SENSE** | Inspects Tier-2 supplier *LiCore Materials* (65% share). Detects port congestion signal. Flags **`HIGH` concentration risk (90/100)** with explainable justification. |
| **3** | **`SHP-1002`** | **Robotics MCU Chip Shortage** (Hsinchu → Bengaluru) | **RECOVER** | Evaluates secondary stock and matches 120 certified Grade A recovered chips at *Circular Electronics Lab* (45 km away). Click **Approve Sourcing**. |

**Audit Verification**: Check the **Compliance & Human-in-the-Loop Audit Log** panel at the bottom of the dashboard. Each approved or rejected action appears instantly with an ID, timestamp, and approver identity.

---

## 🔌 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Healthcheck and active pillar verification |
| `GET` | `/api/shipments` | Retrieves all registered active shipments |
| `GET` | `/api/sense/{component_id}` | Runs SENSE agent on a component's multi-tier supplier tree |
| `GET` | `/api/adapt/{shipment_id}` | Runs ADAPT agent against live route disruptions and perishability |
| `GET` | `/api/recover/{component_id}` | Runs RECOVER agent against circular recovery inventory |
| `POST` | `/api/approve` | Submits human decision (`approved`/`rejected`) for an agent proposal |
| `GET` | `/api/audit` | Retrieves the immutable audit ledger entries |

---

## ⚙️ Configuration & Pluggable LLM

AEGIS operates 100% offline with structured template reasoning out-of-the-box. To enable generative natural-language summaries:

```bash
# Optional: Set Anthropic API Key
export ANTHROPIC_API_KEY="sk-ant-api..."    # Linux / macOS
$env:ANTHROPIC_API_KEY="sk-ant-api..."       # Windows PowerShell
```

### SAP Learning Hub & Enterprise Integration Touchpoints
- **SAP Generative AI Hub**: Swap the handler in `backend/agents/llm.py` with SAP Generative AI Hub's SDK/REST endpoint using prompt templates from the *SAP Learning Hub*.
- **SAP HANA Cloud**: Transition `backend/audit_log.json` to an enterprise SAP HANA Cloud columnar table for enterprise-grade compliance and reporting.

---

## 👥 Team & Hackathon Context

- **Team**: Nexus Polaris
- **Track / ID**: HS26-112
- **Focus**: Intelligent Supply Chain Resilience, Autonomous Explainable AI, Circular Logistics
