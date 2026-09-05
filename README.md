<div align="center">

# 🧠 Razorpay Recovery Brain

### *AI-powered revenue recovery agent for the Razorpay ecosystem*

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-SDK-072654?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com)

<br/>

[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.7-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)

<br/>

> **Detects** failed payments → **Diagnoses** root causes → **Plans** the right intervention → **Enforces** compliance rules → **Executes** recovery → **Audits** every decision
>
> All on-premise. Zero external AI API calls. Your payment data never leaves your server.

<br/>

</div>

---

## 📌 The Problem

Every second, a payment fails somewhere. A bank timeout. A mandate bounce. A customer who abandoned their cart at checkout. Most merchants find out **three days later — from a spreadsheet.**

| Current Reality | Recovery Brain |
|---|---|
| Retry everything blindly | ML-scored per-payment probability |
| Generic email to every customer | 10 distinct recovery actions matched to failure type |
| No stopping rules | 6 hard policy gates — amount, probability, retry limit, contact limit |
| No audit trail | 7 structured audit events per payment, persisted and queryable |
| Hours to days response time | Under 2 seconds, end to end |
| Payment data sent to external AI | Zero external model API calls — fully on-premise |

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph UI["🖥️ React Dashboard (Vite + TailwindCSS)"]
        A[Overview & Simulator]
        B[Batch Operations]
        C[Payment Drill-Down]
        D[Promise-to-Pay]
        E[Hinglish Recovery]
        F[Failure Lab]
    end

    subgraph API["⚡ FastAPI Backend"]
        G["/recovery/*"]
        H["/api/v1/dashboard/*"]
        I["/mcp/* (MCP Server)"]
    end

    subgraph PIPELINE["🧠 LangGraph State Machine"]
        J[1. CLASSIFY] --> K[2. PREDICT]
        K --> L[3. DIAGNOSE]
        L --> M[4. PLAN]
        M --> N{5. POLICY GATE}
        N -->|approved| O[6. EXECUTE]
        N -->|blocked| P[POLICY_BLOCKED]
        N -->|permanent| Q[NO_ACTION_REQUIRED]
        N -->|escalate| R[MERCHANT_ESCALATION]
        O --> S[7. VERIFY]
    end

    subgraph TOOLS["🔧 Tool Registry"]
        T[RetryTool]
        U[RecoveryLinkTool]
        V[MandateRetryTool]
        W[B2BReceivablesChaser]
        X[PromiseToPayTool]
        Y[HinglishVoiceTool]
    end

    subgraph DATA["💾 Persistence Layer"]
        Z[(SQLite DB)]
        AA[workflow_runs]
        BB[audit_trails]
    end

    subgraph RAZORPAY["💳 Razorpay API"]
        CC[Payment Fetch]
        DD[Payment Links]
    end

    UI --> API
    API --> PIPELINE
    O --> TOOLS
    TOOLS --> RAZORPAY
    PIPELINE --> DATA
```

---

## 🔄 The 7-Stage Pipeline

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant LG as LangGraph
    participant ML as Random Forest
    participant PG as Policy Guardian
    participant TOOL as Tool Registry
    participant RZP as Razorpay API
    participant DB as SQLite

    C->>API: POST /recovery/analyze/sync
    API->>LG: invoke(initial_state)

    LG->>LG: classify_node → FailureCategory
    Note over LG: 50+ failure reasons mapped<br/>Safe default: TEMPORARY_FAILURE

    LG->>ML: predict_node → recovery_probability
    Note over ML: 200-tree Random Forest<br/>8 features, cached via @lru_cache

    LG->>LG: diagnosis_node → Diagnosis + reason_codes
    LG->>LG: planning_node → RecoveryAction + parameters

    LG->>PG: policy_node → PolicyDecision
    Note over PG: 6 hard rules:<br/>amount, prob, retries, contacts,<br/>permanent failure, fraud

    alt Policy Approved
        LG->>TOOL: execute_node
        TOOL->>RZP: API call (retry / payment link)
        RZP-->>TOOL: result
        LG->>LG: verify_node → recovered_amount
    else Policy Blocked
        LG->>LG: blocked_node → POLICY_BLOCKED
    end

    LG->>DB: save_run (upsert RunRecord + 7x AuditRecord)
    LG-->>API: final_state
    API-->>C: RecoveryAnalyzeResponse
```

---

## 🎯 Recovery Scenarios

```mermaid
mindmap
  root((Recovery Brain))
    Payment Degradation
      bank_timeout → RETRY_LATER
      network_error → RETRY_NOW
      gateway_timeout → RETRY_LATER
    Checkout Drop-off
      cart_abandoned → SEND_RECOVERY_LINK
      session_expired → SEND_RECOVERY_LINK
      inactivity → SEND_RECOVERY_LINK
    Failed Subscriptions
      subscription_failed → MANDATE_RETRY
      mandate_rejected → MANDATE_RETRY
      nach_bounce → MANDATE_RETRY
      Sequence T+1h · T+24h · T+72h
    B2B Receivables
      b2b_overdue → B2B_CHASE
      invoice_overdue → B2B_CHASE
      Escalation reminder → senior_ar → legal
    Promise to Pay
      Repeated customer failures
      3-day commitment window
      Auto follow-ups at 50% and 90%
    Hinglish Recovery
      SMS · Voice · WhatsApp
      Failure-matched templates
      Hindi + English code-switch
    Permanent Failures
      fraud_detected → DO_NOTHING
      closed_account → DO_NOTHING
      chargeback → DO_NOTHING
```

---

## 🛡️ Policy Guardian — The Compliance Gate

```mermaid
flowchart LR
    IN([Recovery Plan]) --> R1{DO_NOTHING\nor ESCALATE?}
    R1 -->|yes| APPROVE1([✅ APPROVED])
    R1 -->|no| R2{PERMANENT\nFAILURE?}
    R2 -->|yes| BLOCK1([🚫 BLOCKED\nPERMANENT_FAILURE])
    R2 -->|no| R3{amount >\n₹10,000?}
    R3 -->|yes| BLOCK2([🚫 BLOCKED\nAMOUNT_LIMIT])
    R3 -->|no| R4{probability <\n0.55?}
    R4 -->|yes| BLOCK3([🚫 BLOCKED\nPROB_TOO_LOW])
    R4 -->|no| R5{retries ≥ 2?}
    R5 -->|yes| BLOCK4([🚫 BLOCKED\nMAX_RETRIES])
    R5 -->|no| R6{contacts ≥ 1?}
    R6 -->|yes| BLOCK5([🚫 BLOCKED\nMAX_CONTACTS])
    R6 -->|no| APPROVE2([✅ APPROVED\nPOLICY_CHECKS_PASSED])

    style APPROVE1 fill:#00D09C,color:#000
    style APPROVE2 fill:#00D09C,color:#000
    style BLOCK1 fill:#FF4757,color:#fff
    style BLOCK2 fill:#FF4757,color:#fff
    style BLOCK3 fill:#FF4757,color:#fff
    style BLOCK4 fill:#FF4757,color:#fff
    style BLOCK5 fill:#FF4757,color:#fff
```

---

## 🔒 Privacy & Security Architecture

```mermaid
graph LR
    subgraph EXTERNAL["🌐 External World"]
        A[Razorpay API\nPayment Links · Fetch]
    end

    subgraph SYSTEM["🔐 Recovery Brain — On-Premise Only"]
        B[FastAPI Server]
        C[Random Forest ML\nlru_cache — loaded once]
        D[Classification Rules\nDeterministic lookup]
        E[Policy Guardian\nHard-coded limits]
        F[(SQLite\nLocal disk only)]
    end

    subgraph NEVER["❌ NEVER Happens"]
        G[OpenAI API]
        H[Anthropic API]
        I[Any LLM API]
        J[Cloud Database Sync]
    end

    B <--> A
    B --> C
    B --> D
    B --> E
    B --> F

    style NEVER fill:#1a0000,stroke:#FF4757,color:#FF4757
    style SYSTEM fill:#001a0d,stroke:#00D09C,color:#00D09C
    style EXTERNAL fill:#001220,stroke:#0DF5E3,color:#0DF5E3
```

> **Zero external AI calls.** The intelligence layer — ML prediction, failure classification, diagnosis, action planning — runs entirely on your infrastructure. No payment metadata is ever sent to OpenAI, Anthropic, or any third-party model provider.

---

## 📊 Dashboard Pages

| Page | Route | What it shows |
|---|---|---|
| 🖥️ **Overview** | `/` | Live metrics, payment simulator, real-time workflow tracker, recovery funnel chart |
| 📋 **Batch Operations** | `/batches` | All processed payments — searchable, with recovered amounts, policy decisions, actions |
| 🔍 **Payment Drill-Down** | `/batches/:runId` | 7-node animated pipeline, full audit timeline, policy reason codes, execution result |
| ⚡ **Batch Recovery** | `/batch-submit` | Submit up to 100 payments, see aggregate risk / predicted / recovered in real time |
| 🤝 **Promise-to-Pay** | `/promise-pay` | Record payment commitments, view deadline + automated follow-up schedule |
| 🎤 **Hinglish Recovery** | `/hinglish` | Dispatch language-native nudges, preview Hinglish message text |
| 🧪 **Failure Lab** | `/failure-lab` | One-click live demo of the complete 7-stage pipeline |
| 🏗️ **System Architecture** | `/architecture` | 4-zone architecture diagram |

---

## 🚀 Quick Start

### Backend

```bash
# Clone and set up
git clone https://github.com/Suchet0312/RazorPayBuildathon.git
cd RazorPayBuildathon

# Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# → Add your Razorpay test keys (optional — mocks work without them)

# Start server
uvicorn app.main:app --reload --port 8000
```

| URL | What's there |
|---|---|
| `http://localhost:8000/docs` | Swagger UI — all 12 endpoints |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/redoc` | ReDoc API reference |

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

> **Works without Razorpay keys.** The tool registry automatically falls back to mock implementations. All 7 pipeline stages run, all audit events are recorded, all dashboard metrics are real.

---

## 🌐 API Reference

```
GET  /health
POST /recovery/analyze              → async fire-and-forget, returns run_id immediately
POST /recovery/analyze/sync         → synchronous, full result with audit trail
POST /recovery/batch                → batch up to 100 payments, aggregate metrics
GET  /recovery/status/{run_id}      → poll async workflow status
POST /recovery/promise-to-pay       → record payment commitment + follow-up schedule
POST /recovery/hinglish             → dispatch Hinglish SMS / voice / WhatsApp nudge
POST /recovery/simulate-failure     → live demo: bank_timeout on ₹4,999 UPI

GET  /api/v1/dashboard/metrics                        → total_processed, revenue_at_risk, recovery_rate
GET  /api/v1/dashboard/recovery-batches               → all runs, summary list
GET  /api/v1/dashboard/recovery-batches/{run_id}      → full drill-down with audit trail
POST /api/v1/dashboard/demo/simulate-failure          → formatted demo result for UI
```

---

## ⚙️ Policy Constants

```python
MAX_AUTO_ACTION_AMOUNT   = 10_000   # ₹ — above this, escalate to merchant for manual review
MIN_RECOVERY_PROBABILITY = 0.55     # below this, block automated action — not worth the cost
MAX_RETRY_ATTEMPTS       = 2        # per payment — stop hammering a bank that keeps declining
MAX_CUSTOMER_CONTACTS    = 1        # per payment — one message max, no spam
```

---

## 🗂️ Project Structure

```
razorpay-recovery-brain/
│
├── app/
│   ├── agents/                  # 🤖 diagnosis_agent · recovery_planner · policy_guardian
│   ├── api/
│   │   ├── routes/              # ⚡ recovery · dashboard · health
│   │   └── schemas/             # 📐 requests · responses · dashboard schemas
│   ├── core/                    # ⚙️  config · database · logging
│   ├── data/
│   │   ├── generators/          # 🏭 synthetic payment data generator
│   │   ├── synthetic/           # 📊 payments.csv · demo_batch.csv
│   │   └── models.py            # 🗄️  SQLAlchemy ORM (RunRecord · AuditRecord)
│   ├── domain/
│   │   ├── enums/               # 📌 PaymentStatus · FailureCategory · RecoveryAction · AuditStage
│   │   └── models/              # 📦 PaymentRiskRecord · Diagnosis · RecoveryPlan · PolicyDecision
│   ├── integrations/            # 🔌 razorpay_client.py (singleton)
│   ├── intelligence/
│   │   ├── artifacts/           # 🧠 recovery_model.joblib (trained RF)
│   │   ├── classification/      # 🏷️  rules.py — 50+ failure reason mappings
│   │   ├── features/            # 🔧 feature_builder.py — 8 feature dimensions
│   │   └── models/              # 📈 train · predict · evaluate
│   ├── mcp/                     # 🤝 MCP server — 7 tools for AI agent access
│   ├── policies/                # 📜 constants.py — policy thresholds
│   ├── repositories/            # 🗃️  recovery_repository.py — SQLAlchemy upsert
│   ├── services/                # 🔄 recovery · dashboard · promise_to_pay · hinglish
│   ├── tools/                   # 🔧 retry · recovery_link · mandate · b2b · ptp · hinglish
│   └── workflows/               # 🔀 LangGraph: state · graph · nodes · router · verification
│
├── frontend/
│   └── src/
│       ├── pages/               # 8 dashboard pages
│       ├── components/layout/   # Sidebar · Layout
│       ├── services/api.js      # Axios client (dashApi + recoveryApi)
│       ├── PaymentSimulator.jsx # Payment failure form
│       └── WorkflowTracker.jsx  # Live pipeline polling component
│
├── scripts/                     # 🛠️  train_model.py · generate_data.py · inspect_data.py
├── tests/                       # 🧪 unit/ · integration/ · fixtures/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🧪 ML Model Details

```mermaid
graph LR
    subgraph FEATURES["8 Input Features"]
        F1[amount]
        F2[payment_method]
        F3[failure_category]
        F4[attempt_count]
        F5[customer_success_rate]
        F6[prev_retry_success_rate]
        F7[hour_of_day]
        F8[day_of_week]
    end

    subgraph PIPELINE["sklearn Pipeline"]
        P1[ColumnTransformer\nOneHotEncoder for categoricals\nPassthrough for numericals]
        P2[RandomForestClassifier\nn_estimators=200\nclass_weight=balanced\nrandom_state=42]
    end

    subgraph OUTPUT["Output"]
        O1[recovery_probability\nfloat 0.0 → 1.0]
    end

    FEATURES --> P1
    P1 --> P2
    P2 --> O1
```

> Model is loaded **once per process** via `@lru_cache(maxsize=1)`. Call `invalidate_model_cache()` after retraining — next request picks up the new artifact automatically.

---

## 🔑 Environment Variables

```bash
# .env.example
APP_NAME=Razorpay Recovery Brain
APP_VERSION=0.1.0
ENVIRONMENT=development

# Optional — system runs on mocks without these
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📈 Numbers at a Glance

<div align="center">

| Metric | Value |
|:---:|:---:|
| Failure reasons mapped | **50+** |
| ML feature dimensions | **8** |
| Random Forest estimators | **200** |
| Recovery actions available | **10** |
| Policy compliance checks | **6** |
| Audit events per pipeline run | **7** |
| REST API endpoints | **12** |
| MCP tools exposed | **7** |
| Dashboard pages | **8** |
| External AI API calls | **0** |

</div>

---

## 🤝 MCP Integration

Recovery Brain exposes **7 tools** over the [Model Context Protocol](https://modelcontextprotocol.io) — making the entire pipeline accessible to any MCP-compatible AI agent (Claude, custom agents, Kiro):

```
run_recovery_workflow       → full 7-stage pipeline
check_recovery_status       → poll run by run_id
fetch_dashboard_metrics     → aggregated revenue metrics
fetch_recovery_batches      → all runs summary
fetch_payment_details       → full drill-down with audit trail
triage_failure              → quick failure classification only
estimate_recovery_probability → standalone ML prediction
```

```bash
# Install MCP support (optional)
pip install 'mcp[cli]'
# Server auto-mounts at /mcp when installed
```

---

<div align="center">

**Built for Razorpay Buildathon · Track 03 — AI Revenue Recovery**

*Find revenue that's slipping away and win it back*

[![Made with ❤️ in India](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20in-India-FF9933?style=for-the-badge)](https://github.com/Suchet0312/RazorPayBuildathon)

</div>
