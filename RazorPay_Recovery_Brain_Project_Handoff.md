# RazorPay Recovery Brain — Project Continuity & Master Roadmap

**Project status:** Day 7 complete  
**Last validated state:** 73 tests passed  
**Purpose of this document:** Paste or upload this document at the start of future conversations so development can continue without losing project context.

---

# 1. PROJECT VISION

We are building a production-style **Payment Recovery Brain** for failed payment recovery.

The system receives a failed payment, determines what kind of failure occurred, estimates recovery probability/value, diagnoses the situation, proposes a recovery action, passes that action through a strict policy gate, executes only approved actions through controlled tools, verifies the outcome, and records an auditable trail.

The goal is not a simple chatbot. It is an agentic, policy-controlled decision-and-execution system for payment recovery.

Core principle:

    ML predicts.
    Agents reason and plan.
    Policy decides what is allowed.
    Tools execute capabilities.
    Verification confirms outcomes.
    Audit records why and what happened.

---

# 2. TARGET END-TO-END ARCHITECTURE

    Failed Payment Input
            |
            v
    +-------------------+
    | Classification    |
    +-------------------+
            |
            v
    +-------------------+
    | ML Prediction     |
    | Recovery Probability
    | Expected Value
    | Priority Score    |
    +-------------------+
            |
            v
    +-------------------+
    | Diagnosis         |
    +-------------------+
            |
            v
    +-------------------+
    | Recovery Planning |
    +-------------------+
            |
            v
    +-------------------+
    | Policy Guardian   |
    | Approval / Reject |
    +-------------------+
            |
       Conditional Routing
       /       |        \
      v        v         v
  Execute   No Action  Escalate
      |
      v
    Tools
      |
      v
  Verification
      |
      v
  Audit Trail
      |
      v
 API / Observability / UI / Deployment

---

# 3. WHAT WE ARE BUILDING

Project name used internally: **RazorPay Recovery Brain**

Domain: automated recovery orchestration for failed payments.

Typical recovery actions include:

- RETRY_NOW
- RETRY_LATER
- SEND_RECOVERY_LINK
- SUGGEST_ALTERNATE_METHOD
- ESCALATE_TO_MERCHANT
- DO_NOTHING

The system must never allow an execution tool to independently decide policy.

Correct separation:

    Planner proposes action
            |
            v
    Policy validates action
            |
            v
    Router decides allowed path
            |
            v
    Tool Service executes capability

---

# 4. DEVELOPMENT PROGRESSION COMPLETED

## Day 1 — RAG Fundamentals

Completed foundational retrieval concepts and early project groundwork.

Key learning:
- documents
- chunking
- embeddings
- vector search
- retrieval

## Day 2 — Raw RAG

Built raw RAG-style retrieval understanding without hiding the pipeline behind frameworks.

Concepts:
- document ingestion
- chunking
- embedding
- indexing
- retrieval
- generation

## Day 3 — LangChain / Structured Workflows

Introduced framework-based orchestration and structured AI components.

## Day 4 — Hybrid Retrieval + Reranking

Implemented and learned:
- dense retrieval
- lexical/BM25 retrieval
- hybrid retrieval
- reranking
- retrieval evaluation

## Day 5 — Evaluation and Reliability

Added testing and evaluation discipline.

Important lesson:
A working AI pipeline is not enough; it needs measurable correctness and regression protection.

## Day 6 — LangGraph / Agentic Workflow

Moved from linear pipelines to graph-based orchestration.

Built concepts around:
- shared workflow state
- nodes
- edges
- conditional routing
- terminal states
- recovery branches

## Day 7 — Tools, Controlled Execution, Verification, Audit

DAY 7 IS COMPLETE.

Final validated result:

    73 passed

Warnings remain from dependency internals:

    joblib / NumPy deprecation warning

These warnings do not currently fail tests and are not blocking progress.

---

# 5. CURRENT PROJECT ARCHITECTURE

Important application areas:

    app/
    ├── domain/
    │   ├── enums/
    │   └── models/
    │
    ├── tools/
    │   ├── base.py
    │   ├── retry_tool.py
    │   ├── recovery_link_tool.py
    │   ├── alternate_method_tool.py
    │   ├── registry.py
    │   └── service.py
    │
    ├── workflows/
    │   ├── state.py
    │   ├── factory.py
    │   ├── nodes.py
    │   ├── router.py
    │   ├── graph.py
    │   └── verification.py
    │
    └── tests/
        ├── unit/
        └── integration/

Exact file structure may evolve, but preserve the architecture boundaries.

---

# 6. DOMAIN MODELS / IMPORTANT CONTRACTS

## PaymentRiskRecord

Represents the payment and its recovery-relevant information.

Examples of fields used:

- payment_id
- customer_id
- merchant_id
- amount
- currency
- payment_method
- status
- failure_reason
- attempt_count
- event_timestamp
- customer_success_rate
- previous_retry_success_rate
- contact_count
- actual_recovery_outcome

## RecoveryPlan

Contains the proposed recovery action.

Important fields include:

- action
- action_parameters
- reason_codes
- expected_recovery_value
- priority_score

## ExecutionRequest

Represents a controlled request sent from the workflow into the tool layer.

The execution contract includes information such as:

- run_id
- action
- payment_id
- action_parameters

Important design principle:
Tools should receive an explicit execution request rather than being responsible for policy decisions.

## ExecutionResult

Represents the result of a tool execution.

Important fields:

- success
- action
- external_reference_id
- message
- error_code

## VerificationResult

Represents whether recovery was actually confirmed.

Important fields:

- verified
- recovered_amount
- message

## AuditEvent

Audit model includes:

- audit_id
- run_id
- payment_id
- timestamp
- stage
- input_summary
- decision
- reason_codes
- actor
- result
- metadata

---

# 7. WORKFLOW STATE

Current shared LangGraph state is `RecoveryState`.

Important fields include:

## Identity

- run_id

## Input

- payment

## Classification

- classification
- failure_category

## ML prediction

- recovery_probability
- expected_recovery_value
- priority_score

## Agent outputs

- diagnosis
- recovery_plan

## Policy

- policy_decision
- policy_approved

## Execution and verification

- execution_result
- verification_result
- recovered_amount
- workflow_status

## Audit and errors

- audit_trail
- errors

The state is the contract between workflow nodes. New fields should be added deliberately and tested.

---

# 8. CURRENT LANGGRAPH FLOW

The current recovery graph conceptually follows:

    START
      |
      v
    classify
      |
      v
    predict
      |
      v
    diagnose
      |
      v
    plan
      |
      v
    policy
      |
      +-----------------------------+
      |             |               |
      v             v               v
    execute      blocked        no_action
      |                             |
      v                             v
    verify                          END
      |
      v
     END

There is also an escalation terminal path:

    policy
      |
      v
    escalate
      |
      v
     END

Current terminal statuses include:

- EXECUTION_SUCCEEDED
- EXECUTION_FAILED
- RECOVERY_VERIFIED
- RECOVERY_NOT_VERIFIED
- POLICY_BLOCKED
- NO_ACTION_REQUIRED
- MERCHANT_ESCALATION_REQUIRED

Verification is intentionally a separate concept from execution.

Execution success:

    "Did the tool run successfully?"

Verification:

    "Was the payment recovery actually confirmed?"

Do not collapse these concepts together.

---

# 9. DAY 7 TOOL ARCHITECTURE

The Day 7 tool architecture is one of the most important completed parts.

## RecoveryTool

A protocol/interface defines the execution contract.

Tools provide capability only.

Tools do NOT:

- approve actions
- evaluate policy
- decide whether recovery should happen

Tools only execute.

## Implemented Mock Tools

### MockRetryTool

Supports:

- RETRY_NOW
- RETRY_LATER

Returns deterministic mock execution results.

### MockRecoveryLinkTool

Supports:

- SEND_RECOVERY_LINK

### MockAlternateMethodTool

Supports:

- SUGGEST_ALTERNATE_METHOD

### ToolRegistry

Maps recovery actions to the appropriate tool.

Examples:

    RETRY_NOW -> MockRetryTool
    RETRY_LATER -> MockRetryTool
    SEND_RECOVERY_LINK -> MockRecoveryLinkTool
    SUGGEST_ALTERNATE_METHOD -> MockAlternateMethodTool

Unregistered actions must fail safely.

Expected failure behavior for an unregistered tool:

- success = False
- error_code = TOOL_NOT_REGISTERED
- workflow_status = EXECUTION_FAILED
- appropriate error message
- execution audit event

## RecoveryToolService

The workflow delegates execution through the service layer.

Conceptually:

    Workflow
       |
       v
    RecoveryToolService
       |
       v
    ToolRegistry
       |
       v
    Concrete Tool

This prevents the workflow from becoming tightly coupled to individual tool implementations.

---

# 10. EXECUTION BEHAVIOR

The execution node:

1. reads the approved recovery action
2. creates an `ExecutionRequest`
3. delegates to `RecoveryToolService`
4. receives `ExecutionResult`
5. creates an execution audit event
6. updates workflow status

Failure paths include:

## Tool not registered

Expected:

    error_code = TOOL_NOT_REGISTERED

## Tool exception

Expected:

    error_code = TOOL_EXECUTION_ERROR

## Tool returns unsuccessful result

Expected:

    workflow_status = EXECUTION_FAILED

## Tool succeeds

Expected:

    workflow_status = EXECUTION_SUCCEEDED

The graph then proceeds to verification for execution paths.

---

# 11. VERIFICATION

Verification is implemented in:

    app/workflows/verification.py

The verification node:

1. receives execution result
2. checks whether execution succeeded
3. determines verification outcome
4. sets recovered amount
5. creates verification audit event
6. updates workflow status

Current deterministic behavior:

If execution failed:

    verified = False
    recovered_amount = 0.0
    workflow_status = RECOVERY_NOT_VERIFIED

If execution succeeded:

    recovered_amount = recovery_plan.expected_recovery_value
    verified = True
    workflow_status = RECOVERY_VERIFIED

This is currently mock/deterministic verification.

Future production work may replace this with:

- payment status lookup
- webhook/event confirmation
- asynchronous polling
- reconciliation
- delayed verification

Do not remove the verification layer; improve its implementation later.

---

# 12. AUDIT ARCHITECTURE

Audit stages currently include:

- INGEST
- CLASSIFICATION
- PREDICTION
- DIAGNOSIS
- PLANNING
- POLICY_GATE
- EXECUTION
- VERIFICATION
- AUDIT

Day 7 implemented execution and verification audit events.

## Execution Audit

Created when execution:

- succeeds
- fails
- throws an exception
- has no registered tool

## Verification Audit

Created when verification:

- succeeds
- fails

Important requirement:

The audit trail must preserve both execution and verification events during graph execution.

Expected concept:

    audit_trail
      |
      +-- execution event
      |
      +-- verification event

Do not accidentally overwrite earlier audit entries when extending nodes.

---

# 13. TESTING STATUS

Last confirmed command:

    python -m pytest -q

Last confirmed result:

    73 passed

No test failures.

Current warnings are dependency-level deprecation warnings, primarily involving NumPy/joblib.

Do not spend Day 8 debugging these warnings unless they become actual failures.

Testing philosophy going forward:

- add tests when adding architecture
- preserve old tests
- run full suite after meaningful changes
- test failure branches, not only happy paths
- test policy boundaries
- test API contracts once API layer is added

---

# 14. IMPORTANT LESSONS FROM DAY 7

## Never let tools decide policy

Wrong:

    Tool checks if action should be allowed
    Tool executes if it thinks it is safe

Correct:

    Planner proposes
        |
        v
    Policy approves/rejects
        |
        v
    Router selects path
        |
        v
    Tool executes

## Execution is not verification

A retry API call succeeding does not automatically prove payment recovery.

## Service layer improves separation

The workflow should orchestrate.

The service should coordinate capability lookup/execution.

Tools should perform concrete operations.

## Auditability must be designed into the system

Do not treat logging as sufficient.

Audit events should capture structured facts:

- actor
- stage
- decision
- reason codes
- result
- metadata

---

# 15. DAY 8 — NEXT PHASE

DAY 8 WILL FOCUS ON:

# Production API + Observability + Service Integration

The Recovery Brain is currently primarily an internal Python workflow.

Day 8 begins turning it into a usable backend service.

Target:

    Client / UI / API Consumer
              |
              v
         FastAPI Layer
              |
              v
       Request Validation
              |
              v
       Recovery Workflow
              |
              v
    ML + Agents + Policy + Tools
              |
              v
       Verification + Audit
              |
              v
        Structured Response

---

# 16. DAY 8 DETAILED PLAN

## Phase 1 — API Architecture

Create a clean API boundary.

Likely structure:

    app/
    ├── api/
    │   ├── routes/
    │   ├── schemas/
    │   └── dependencies/
    │
    ├── services/
    ├── workflows/
    ├── domain/
    └── tools/

Exact naming can evolve, but keep domain/workflow/tool separation.

## Phase 2 — FastAPI Application

Create the application entry point.

Likely responsibilities:

- application creation
- router registration
- health endpoint
- configuration loading

Potential endpoints:

    GET /health

    POST /recovery/analyze

The exact API design should be finalized before implementation.

## Phase 3 — Request/Response Contracts

Define API schemas separate from internal domain models when appropriate.

Possible request:

    {
      "payment_id": "...",
      "customer_id": "...",
      "merchant_id": "...",
      "amount": 5000,
      ...
    }

Possible response:

    {
      "run_id": "...",
      "classification": "...",
      "recovery_probability": ...,
      "recovery_plan": ...,
      "policy_decision": ...,
      "execution_result": ...,
      "verification_result": ...,
      "workflow_status": "...",
      "recovered_amount": ...
    }

Do not expose unnecessary internal implementation details without deliberate design.

## Phase 4 — Workflow Service Boundary

Avoid placing all graph invocation logic directly inside the API route.

Preferred:

    API Route
       |
       v
    RecoveryService / Application Service
       |
       v
    create_recovery_state()
       |
       v
    graph.invoke()
       |
       v
    structured response

This keeps HTTP concerns separate from business orchestration.

## Phase 5 — Error Handling

Introduce consistent API error behavior.

Consider:

- validation errors
- workflow execution failures
- unexpected internal errors
- domain errors

Avoid leaking raw stack traces.

## Phase 6 — Observability

Add structured observability.

Potential areas:

- request/run ID
- payment ID
- workflow status
- node timings
- execution outcomes
- verification outcomes
- errors

Important distinction:

Logging != Audit Trail.

Logs help operators/debugging.

Audit events explain business decisions and system actions.

Keep both concepts separate.

## Phase 7 — API Tests

Add tests for:

- health endpoint
- valid recovery request
- invalid request
- policy blocked response
- no action response
- successful execution/verification response
- internal error handling

## Phase 8 — End-to-End Validation

Run:

    python -m pytest -q

Also manually test API requests.

---

# 17. LIKELY DAY 8 IMPLEMENTATION ORDER

Recommended sequence:

1. inspect current project structure
2. decide API/service folder structure
3. add FastAPI application entry point
4. add health endpoint
5. create request schema
6. create response schema
7. create RecoveryService/application service
8. connect route to workflow
9. add exception handling
10. add structured logging/observability
11. add API tests
12. run full suite
13. manual end-to-end request test

Do not jump directly into deployment before the API is stable.

---

# 18. LATER ROADMAP AFTER DAY 8

## Day 9 — Persistence and Real Infrastructure

Likely work:

- database persistence
- audit storage
- run history
- payment/recovery records
- configuration management

Potential technologies should be chosen based on project requirements rather than adding tools for the sake of complexity.

## Day 10 — Async / Realistic Execution

Potential:

- asynchronous execution
- background jobs
- delayed verification
- retries
- idempotency
- webhook/event handling

## Day 11 — Production Reliability

Potential:

- idempotency keys
- retry strategy
- timeout handling
- circuit breakers
- failure recovery
- stronger validation
- concurrency considerations

## Day 12 — Frontend/UI

Build a useful interface for:

- submitting payment failures
- viewing workflow decisions
- viewing policy decisions
- execution status
- verification status
- audit timeline

## Day 13 — Deployment

Potential:

- containerization
- environment variables
- production configuration
- cloud deployment
- CI/CD basics

## Day 14 — Final Polish

Potential:

- architecture documentation
- README
- screenshots
- API documentation
- demo flow
- final testing
- portfolio-quality presentation

The exact schedule may be adjusted based on implementation complexity, but the architectural sequence should remain stable.

---

# 19. NON-NEGOTIABLE ARCHITECTURE RULES

1. Do not let tools make policy decisions.
2. Do not bypass the policy gate.
3. Keep workflow orchestration separate from execution capability.
4. Keep execution separate from verification.
5. Keep audit events structured.
6. Preserve backward compatibility when possible.
7. Run tests after meaningful changes.
8. Add tests for failure paths.
9. Prefer explicit contracts/models over loose dictionaries at service boundaries.
10. Avoid unnecessary framework complexity.
11. Build incrementally; do not rewrite working architecture without reason.
12. Keep the project production-oriented, not tutorial-oriented.

---

# 20. START-OF-NEXT-CONVERSATION INSTRUCTIONS

When starting a new conversation, provide this document and say:

    Continue the RazorPay Recovery Brain project from this handoff.
    Day 7 is complete with 73 passing tests.
    We are starting Day 8: Production API + Observability + Service Integration.
    Follow the roadmap in this document and do not restart or redesign completed work unnecessarily.

Then the assistant should:

1. review this handoff
2. identify current implementation status
3. begin Day 8 from Phase 1
4. proceed incrementally
5. give exact files/code to modify
6. wait for test results after major steps
7. preserve the completed architecture

---

# 21. CURRENT CHECKPOINT

FINAL CHECKPOINT BEFORE DAY 8:

    Day 7: COMPLETE
    Tests: 73 passed
    Workflow: Operational
    Tools: Implemented
    Tool service: Implemented
    Policy-controlled execution: Implemented
    Verification: Implemented
    Execution audit: Implemented
    Verification audit: Implemented
    Audit trail: Preserved
    Next phase: FastAPI + Production API + Observability

Do not restart Day 7.

Continue directly with Day 8.

