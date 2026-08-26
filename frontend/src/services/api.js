import axios from 'axios';

const BASE = 'http://localhost:8000';

// ── Dashboard API (prefixed /api/v1) ──────────────────────────────────────
const dashApi = axios.create({
  baseURL: `${BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

// ── Recovery API (no /api/v1 prefix) ─────────────────────────────────────
const recoveryApi = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ── Dashboard endpoints ───────────────────────────────────────────────────
export const getMetrics       = ()        => dashApi.get('/dashboard/metrics').then(r => r.data);
export const getBatches       = ()        => dashApi.get('/dashboard/recovery-batches').then(r => r.data);
export const getPaymentDetails = (runId)  => dashApi.get(`/dashboard/recovery-batches/${runId}`).then(r => r.data);
export const simulateFailureDemo = ()     => dashApi.post('/dashboard/demo/simulate-failure').then(r => r.data);

// kept for backward compat with existing FailureDemo page
export const simulateFailure  = simulateFailureDemo;

// ── Recovery endpoints ────────────────────────────────────────────────────

/** Async fire-and-forget — returns { run_id, workflow_status: "PENDING" } */
export const analyzePayment   = (payload) => recoveryApi.post('/recovery/analyze', payload).then(r => r.data);

/** Synchronous — returns full result including audit trail */
export const analyzePaymentSync = (payload) => recoveryApi.post('/recovery/analyze/sync', payload).then(r => r.data);

/** Run up to 100 payments through the pipeline in one call */
export const analyzeBatch     = (payload) => recoveryApi.post('/recovery/batch', payload).then(r => r.data);

/** Poll status of an async run */
export const getRunStatus     = (runId)   => recoveryApi.get(`/recovery/status/${runId}`).then(r => r.data);

/** Record a customer promise-to-pay commitment */
export const recordPromiseToPay = (payload) => recoveryApi.post('/recovery/promise-to-pay', payload).then(r => r.data);

/** Dispatch a Hinglish voice/SMS recovery nudge */
export const sendHinglishRecovery = (payload) => recoveryApi.post('/recovery/hinglish', payload).then(r => r.data);

/** Run the real bank_timeout scenario end-to-end */
export const simulateRealFailure = () => recoveryApi.post('/recovery/simulate-failure').then(r => r.data);

/** Health check */
export const getHealth        = ()        => recoveryApi.get('/health').then(r => r.data);

export default recoveryApi;
