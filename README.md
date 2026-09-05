# Razorpay Recovery Brain

> **AI-powered revenue recovery agent** — detects failed payments, diagnoses root causes, selects the right intervention, enforces compliance rules, executes the recovery, and produces a complete audit trail. All on-premise. Zero external AI API calls.

---

## What It Does

When a payment fails, Recovery Brain runs a 7-stage agentic pipeline in under 2 seconds:

```
CLASSIFY → PREDICT → DIAGNOSE → PLAN → POLICY GATE → EXECUTE → VERIFY
```

| Stage | What happens |
|---|---|
| **Classify** | Maps 50+ failure reasons into 4 categories (temporary, customer action, abandonment, permanent) |
| **Predict** | Random Forest ML model scores recovery probability (0–1) using 8 payment features |
| **Diagnose** | Builds a structured explanation with reason codes and confidence score |
| **Plan** | Selects exactly one recovery action from 10 options based on failure type |
| **Policy Gate** | 6 hard compliance rules — blocks if amount > ₹10k, prob < 0.55, retries ≥ 2, contacts ≥ 1 |
| **Execute** | Calls Razorpay API (retry, payment link, mandate sequence, B2B chase, Hinglish SMS) |
| **Verify** | Confirms recovery and records the recovered amount |

Every stage emits a structured `AuditEvent` — persisted to SQLite, queryable via API, visualised in the dashboard.

---

## Recovery Scenarios Covered

- **Payment degradation → root cause → recovery action**
- **Checkout drop-off recovery** — Razorpay Payment Link sent automatically
- **Failed subscription recovery** — Mandate retry at T+1h / T+24h / T+72h
- **B2B receivables chaser** — Escalation: reminder → senior AR → legal
- **Mandate retry sequencer** — NACH / ECS / UPI AutoPay bounce handling
- **Hinglish voice recovery** — SMS / Voice / WhatsApp in Hindi+English
- **Promise-to-pay tracker** — Commitment capture with automated follow-ups

---

## Privacy & Security

- **Zero external AI API calls** — the Random Forest runs locally, no payment data sent to OpenAI / Anthropic / any external provider
- **On-premise database** — SQLite, no cloud sync
- **No credentials stored** — only payment IDs, failure reasons, and amounts; raw card / bank details never enter this system
- **Hard contact limits** — policy layer enforces max 1 customer contact per payment at the code level
- **Full audit trail** — every decision logged with reason codes and timestamps; GDPR-ready

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, LangGraph |
| ML | scikit-learn (Random Forest), pandas, joblib |
| Database | SQLAlchemy + SQLite |
| Razorpay | razorpay Python SDK (Payment Links, retries) |
| Frontend | React 19, Vite 8, TailwindCSS 4, Recharts, Framer Motion |
| Protocol | MCP (Model Context Protocol) — 7 tools exposed to AI agents |

---

## Quick Start

### Backend

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Add your Razorpay test keys to .env

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

---

## API Endpoints

```
GET  /health
POST /recovery/analyze              — async, returns run_id
POST /recovery/analyze/sync         — synchronous full result
POST /recovery/batch                — process up to 100 payments
GET  /recovery/status/{run_id}      — poll status
POST /recovery/promise-to-pay       — record payment commitment
POST /recovery/hinglish             — dispatch Hinglish recovery nudge
POST /recovery/simulate-failure     — demo bank_timeout scenario

GET  /api/v1/dashboard/metrics
GET  /api/v1/dashboard/recovery-batches
GET  /api/v1/dashboard/recovery-batches/{run_id}
POST /api/v1/dashboard/demo/simulate-failure
```

---

## Dashboard Pages

| Page | What it shows |
|---|---|
| **Overview** | Live metrics, payment simulator, real-time workflow tracker, recovery funnel chart |
| **Batch Operations** | All processed payments — searchable, with recovered amounts and policy decisions |
| **Batch Recovery** | Submit up to 8 scenarios at once, see aggregate risk / predicted / recovered |
| **Payment Drill-Down** | 7-node pipeline diagram, full audit timeline, policy reason codes, execution result |
| **Promise-to-Pay** | Record commitments, view deadline and follow-up schedule |
| **Hinglish Recovery** | Dispatch language-native recovery nudges, preview the generated message |
| **Failure Lab** | One-click live demo of the complete pipeline |
| **System Architecture** | 4-zone architecture diagram |

---

## Policy Constants

```python
MAX_AUTO_ACTION_AMOUNT   = 10_000   # ₹ — above this, escalate to merchant
MIN_RECOVERY_PROBABILITY = 0.55     # below this, block automated action
MAX_RETRY_ATTEMPTS       = 2        # per payment
MAX_CUSTOMER_CONTACTS    = 1        # per payment
```

---

## Project Structure

```
app/
├── agents/          # diagnosis, planner, policy guardian
├── api/             # routes, schemas
├── core/            # config, database, logging
├── data/            # ORM models, synthetic data generator
├── domain/          # Pydantic models, enums
├── intelligence/    # classification rules, feature engineering, ML train/predict
├── integrations/    # Razorpay client
├── mcp/             # Model Context Protocol server + tools
├── policies/        # policy constants
├── repositories/    # SQLAlchemy data access
├── services/        # recovery, dashboard, promise-to-pay, hinglish
├── tools/           # retry, recovery link, mandate, B2B, PTP, hinglish tools
└── workflows/       # LangGraph state, graph, nodes, router, verification

frontend/
├── src/
│   ├── pages/       # 8 dashboard pages
│   ├── components/  # layout, sidebar
│   ├── services/    # api.js (axios)
│   └── PaymentSimulator.jsx / WorkflowTracker.jsx

scripts/             # data generation and model training utilities
```
