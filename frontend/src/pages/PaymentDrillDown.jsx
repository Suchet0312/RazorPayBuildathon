import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPaymentDetails } from '../services/api';
import {
  ArrowLeft, BrainCircuit, ShieldCheck, Activity,
  TerminalSquare, AlertTriangle, CheckCircle,
} from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

// Backend audit stage values → display labels
const PIPELINE_STAGES = [
  { id: 'classification', label: 'CLASSIFICATION' },
  { id: 'prediction',     label: 'ML PREDICTION'  },
  { id: 'diagnosis',      label: 'AI DIAGNOSIS'   },
  { id: 'planning',       label: 'RECOVERY PLAN'  },
  { id: 'policy_gate',    label: 'POLICY GATE'    },
  { id: 'execution',      label: 'EXECUTION'      },
  { id: 'verification',   label: 'VERIFICATION'   },
];

const SUCCESS_DECISIONS = new Set([
  'approved', 'success', 'classified', 'plan_selected',
  'probability_computed', 'diagnosis_complete',
]);
const FAIL_DECISIONS = new Set(['failed', 'blocked']);

const PipelineNode = ({ label, active, decision, delay }) => {
  const isFail    = FAIL_DECISIONS.has(decision);
  const isSuccess = SUCCESS_DECISIONS.has(decision);
  let color = 'bg-gray-800 border-gray-600 text-gray-500';
  if (active) {
    if (isFail)    color = 'bg-rp-red/20 border-rp-red text-rp-red glow-red';
    else if (isSuccess) color = 'bg-rp-green/20 border-rp-green text-rp-green glow-green';
    else           color = 'bg-rp-cyan/20 border-rp-cyan text-rp-cyan glow-cyan';
  }
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      className="flex flex-col items-center relative z-10 w-24"
    >
      <div className={clsx('w-12 h-12 rounded flex items-center justify-center border-2 mb-2 transition-colors duration-500', color)}>
        {isFail ? <AlertTriangle size={20} /> : isSuccess ? <CheckCircle size={20} /> : <BrainCircuit size={20} />}
      </div>
      <span className="text-[9px] font-mono text-center tracking-widest leading-tight text-gray-400 h-8">{label}</span>
    </motion.div>
  );
};

export default function PaymentDrillDown() {
  const { runId: rawRunId } = useParams();
  const runId = rawRunId ? decodeURIComponent(rawRunId) : null;
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    if (!runId) return;
    getPaymentDetails(runId)
      .then(setData)
      .catch(err => {
        console.error('Drill-down fetch error:', err);
        setError(err?.response?.data?.detail || 'Failed to load run data.');
      })
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading)
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <Activity className="text-rp-cyan animate-spin" size={32} />
          <span className="font-mono text-sm text-rp-cyan tracking-widest">DECRYPTING INVESTIGATION DATA...</span>
        </div>
      </div>
    );

  if (error)
    return (
      <div className="space-y-4">
        <Link to="/batches" className="text-rp-cyan hover:text-white flex items-center gap-2 font-mono text-xs transition-colors">
          <ArrowLeft size={14} /> BACK TO BATCHES
        </Link>
        <div className="bg-rp-red/10 border border-rp-red rounded-lg p-6 font-mono text-xs text-rp-red">
          ERROR: {error}<br /><span className="text-gray-500">run_id: {runId}</span>
        </div>
      </div>
    );

  if (!data)
    return (
      <div className="space-y-4">
        <Link to="/batches" className="text-rp-cyan hover:text-white flex items-center gap-2 font-mono text-xs transition-colors">
          <ArrowLeft size={14} /> BACK TO BATCHES
        </Link>
        <div className="text-rp-red font-mono text-sm">Run not found: {runId}</div>
      </div>
    );

  // ── Safe destructure ──────────────────────────────────────────────────
  const pinfo  = (data.payment_info  && typeof data.payment_info  === 'object') ? data.payment_info  : {};
  const intel  = (data.intelligence  && typeof data.intelligence  === 'object') ? data.intelligence  : {};
  const diag   = (data.diagnosis     && typeof data.diagnosis     === 'object') ? data.diagnosis     : {};
  const rp     = (data.recovery_plan && typeof data.recovery_plan === 'object') ? data.recovery_plan : {};
  const pg     = (data.policy_guardian && typeof data.policy_guardian === 'object') ? data.policy_guardian : {};
  const ex     = (data.execution     && typeof data.execution     === 'object') ? data.execution     : {};
  const trail  = Array.isArray(data.audit_trail) ? data.audit_trail : [];
  const status = data.workflow_status || 'UNKNOWN';

  // ── Field extraction ──────────────────────────────────────────────────
  const planAction   = rp.action || (status === 'NO_ACTION_REQUIRED' ? 'do_nothing' : null);
  const planParams   = rp.action_parameters || {};
  const planExpected = rp.expected_recovery_value ?? null;

  // policy_guardian: { approved: bool, reason_codes: [...], reason: "..." }
  const policyApproved = pg.approved !== undefined ? pg.approved
    : status === 'POLICY_BLOCKED' ? false
    : ['RECOVERY_VERIFIED','EXECUTION_SUCCEEDED','RECOVERY_NOT_VERIFIED','EXECUTION_FAILED'].includes(status) ? true
    : null;
  const policyReason  = pg.reason || '';
  const policyReasons = Array.isArray(pg.reason_codes) ? pg.reason_codes : [];

  const execSuccess = ex.success ?? null;
  const execRef     = ex.external_reference_id ?? null;
  const execMsg     = ex.message || '';
  const execMeta    = ex.metadata || {};

  // ── Pipeline stage map ────────────────────────────────────────────────
  const stageMap = {};
  trail.forEach(a => { stageMap[a.stage] = a; });

  // ── Status badge colour ───────────────────────────────────────────────
  const statusColor = {
    RECOVERY_VERIFIED:            'text-rp-green border-rp-green',
    EXECUTION_SUCCEEDED:          'text-rp-green border-rp-green',
    POLICY_BLOCKED:               'text-rp-red border-rp-red',
    NO_ACTION_REQUIRED:           'text-rp-amber border-rp-amber',
    MERCHANT_ESCALATION_REQUIRED: 'text-rp-amber border-rp-amber',
    ERROR:                        'text-rp-red border-rp-red',
  }[status] || 'text-gray-400 border-gray-600';

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <Link to="/batches" className="text-rp-cyan hover:text-white flex items-center gap-2 font-mono text-xs mb-4 transition-colors">
          <ArrowLeft size={14} /> BACK TO BATCHES
        </Link>
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <TerminalSquare className="text-rp-magenta" /> PAYMENT INVESTIGATOR
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          DEEP DIVE INTO RECOVERY INTELLIGENCE &amp; AUDIT TRAIL
        </p>
      </div>

      {/* Pipeline diagram */}
      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-8 relative overflow-hidden">
        <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-8">AI RECOVERY PIPELINE</h3>
        <div className="flex justify-between items-start relative">
          <div className="absolute top-6 left-12 right-12 h-0.5 bg-[#1e1e24] -z-0" />
          {PIPELINE_STAGES.map((s, i) => {
            const a = stageMap[s.id];
            return (
              <PipelineNode key={s.id} label={s.label} active={!!a} decision={a?.decision || ''} delay={i * 0.1} />
            );
          })}
        </div>
        <div className="mt-6 text-center">
          <span className={`font-mono text-xs font-bold border px-3 py-1 rounded ${statusColor}`}>
            {status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Column 1: Payment info + intelligence */}
        <div className="space-y-6">
          <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
            <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4 border-b border-[#1e1e24] pb-2">PAYMENT INFORMATION</h3>
            <div className="space-y-3 font-mono text-sm">
              {[
                ['PAYMENT_ID',   pinfo.payment_id,        'text-rp-cyan'],
                ['AMOUNT',       pinfo.amount != null ? `₹${Number(pinfo.amount).toLocaleString()}` : '—', 'text-white'],
                ['METHOD',       pinfo.payment_method,    'text-white'],
                ['FAILURE',      pinfo.failure_reason,    'text-rp-red'],
                ['ATTEMPTS',     pinfo.attempt_count,     'text-white'],
                ['CUSTOMER_SR',  pinfo.customer_success_rate != null ? `${(pinfo.customer_success_rate*100).toFixed(0)}%` : '—', 'text-white'],
              ].map(([k, v, c]) => (
                <div key={k} className="flex justify-between items-start gap-2">
                  <span className="text-gray-500 shrink-0">{k}</span>
                  <span className={`${c} text-right break-all`}>{v ?? '—'}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
            <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4 border-b border-[#1e1e24] pb-2 flex items-center gap-2">
              <BrainCircuit size={14} className="text-rp-magenta" /> INTELLIGENCE
            </h3>
            <div className="space-y-3 font-mono text-sm">
              <div className="flex justify-between"><span className="text-gray-500">CLASSIFICATION</span>
                <span className="text-rp-cyan">{intel.classification || '—'}</span>
              </div>
              <div className="flex justify-between"><span className="text-gray-500">REC_PROB</span>
                <span className={intel.recovery_probability > 0.7 ? 'text-rp-green' : intel.recovery_probability > 0.4 ? 'text-rp-amber' : 'text-rp-red'}>
                  {intel.recovery_probability != null ? `${(intel.recovery_probability*100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div className="flex justify-between"><span className="text-gray-500">EXPECTED_VALUE</span>
                <span className="text-white">
                  {intel.expected_recovery_value != null
                    ? `₹${Number(intel.expected_recovery_value).toLocaleString()}`
                    : intel.recovery_probability != null && pinfo.amount != null
                    ? `₹${(pinfo.amount * intel.recovery_probability).toFixed(0)}`
                    : '—'}
                </span>
              </div>
              {intel.priority_score != null && (
                <div className="flex justify-between"><span className="text-gray-500">PRIORITY</span>
                  <span className="text-white">{Number(intel.priority_score).toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Column 2: Diagnosis + Plan + Policy + Execution */}
        <div className="space-y-6">
          <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
            <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4 border-b border-[#1e1e24] pb-2">AI DIAGNOSIS &amp; PLAN</h3>
            <div className="space-y-4 font-mono text-sm">
              {diag.summary && (
                <div>
                  <div className="text-gray-500 text-xs mb-1">DIAGNOSIS_SUMMARY</div>
                  <div className="text-gray-300 bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-xs leading-relaxed">{diag.summary}</div>
                </div>
              )}
              <div>
                <div className="text-gray-500 text-xs mb-1">RECOMMENDED_ACTION</div>
                <div className="text-rp-cyan font-bold uppercase tracking-wide">{planAction || '—'}</div>
              </div>
              {Object.keys(planParams).length > 0 && (
                <div>
                  <div className="text-gray-500 text-xs mb-1">ACTION_PARAMS</div>
                  <div className="bg-[#1a1a24] p-2 rounded border border-[#2a2a35] text-xs text-gray-400">
                    {Object.entries(planParams).map(([k, v]) => (
                      <div key={k}><span className="text-gray-600">{k}: </span>{JSON.stringify(v)}</div>
                    ))}
                  </div>
                </div>
              )}
              {planExpected != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500 text-xs">EXPECTED_RECOVERY</span>
                  <span className="text-rp-green font-bold">₹{Number(planExpected).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Policy Guardian */}
          <div className={clsx('border rounded-lg p-6 relative overflow-hidden',
            policyApproved === true  ? 'bg-[#0a0a0b] border-rp-green/50' :
            policyApproved === false ? 'bg-[#0a0a0b] border-rp-red/50'   :
            'bg-[#121214] border-[#1e1e24]'
          )}>
            {policyApproved === true  && <div className="absolute inset-0 bg-rp-green/5 pointer-events-none" />}
            {policyApproved === false && <div className="absolute inset-0 bg-rp-red/5 pointer-events-none" />}
            <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4 border-b border-[#1e1e24]/30 pb-2 flex items-center gap-2 relative z-10">
              <ShieldCheck size={14} className={policyApproved === true ? 'text-rp-green' : policyApproved === false ? 'text-rp-red' : 'text-gray-400'} />
              POLICY GUARDIAN
            </h3>
            <div className="relative z-10">
              <div className={clsx('text-xl font-bold tracking-widest mb-3 font-mono',
                policyApproved === true  ? 'text-rp-green' :
                policyApproved === false ? 'text-rp-red'   : 'text-gray-500'
              )}>
                {policyApproved === true ? 'APPROVED' : policyApproved === false ? 'BLOCKED' : 'PENDING'}
              </div>
              {policyReason && (
                <div className="text-xs text-gray-400 font-mono mb-3 leading-relaxed">{policyReason}</div>
              )}
              {policyApproved === false && policyReasons.length > 0 && (
                <div className="bg-rp-red/10 border border-rp-red/30 rounded p-3">
                  <div className="text-rp-red font-mono text-xs mb-2">REASON_CODES</div>
                  <ul className="list-disc pl-4 text-rp-red/80 font-mono text-xs space-y-1">
                    {policyReasons.map(c => <li key={c}>{c}</li>)}
                  </ul>
                </div>
              )}
              {policyApproved === false && policyReasons.length === 0 && (
                <div className="bg-rp-red/10 border border-rp-red/30 rounded p-3 text-rp-red/70 font-mono text-xs">
                  Policy blocked this action. Check audit trail for reason codes.
                </div>
              )}
            </div>
          </div>

          {/* Execution result */}
          {execSuccess != null && (
            <div className={clsx('border rounded-lg p-6',
              execSuccess ? 'bg-[#0a0a0b] border-rp-green/30' : 'bg-[#0a0a0b] border-rp-red/30'
            )}>
              <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-3 border-b border-[#1e1e24]/30 pb-2">EXECUTION RESULT</h3>
              <div className="space-y-2 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">STATUS</span>
                  <span className={execSuccess ? 'text-rp-green font-bold' : 'text-rp-red font-bold'}>
                    {execSuccess ? 'SUCCESS' : 'FAILED'}
                  </span>
                </div>
                {execRef && (
                  <div className="flex justify-between gap-4">
                    <span className="text-gray-500 shrink-0">REF_ID</span>
                    <span className="text-gray-300 text-right break-all">{execRef}</span>
                  </div>
                )}
                {execMsg && <div className="text-gray-400 mt-2 leading-relaxed">{execMsg}</div>}
                {execMeta?.payment_link_url && (
                  <a href={execMeta.payment_link_url} target="_blank" rel="noopener noreferrer"
                    className="block mt-2 text-rp-cyan underline break-all text-[10px]">
                    {execMeta.payment_link_url}
                  </a>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Column 3: Audit trail */}
        <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6 max-h-[720px] overflow-y-auto">
          <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4 sticky top-0 bg-[#121214] pb-2 border-b border-[#1e1e24] z-10">
            AUDIT TIMELINE ({trail.length} events)
          </h3>
          {trail.length === 0 ? (
            <div className="text-center py-10 text-gray-600 font-mono text-xs">
              No audit records for this run.<br />
              Workflow status: <span className="text-rp-amber">{status}</span>
            </div>
          ) : (
            <div className="space-y-3">
              {trail.map((audit, i) => {
                const isBlock = audit.decision === 'blocked' || audit.decision === 'failed';
                const isOk    = SUCCESS_DECISIONS.has(audit.decision);
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="bg-[#1a1a24] border border-[#2a2a35] rounded p-3 hover:border-rp-cyan/30 transition-colors"
                  >
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="font-mono text-[10px] text-rp-cyan font-bold tracking-wider">
                        {(audit.stage || '').toUpperCase()}
                      </span>
                      <span className="font-mono text-[9px] text-gray-600">
                        {audit.timestamp ? new Date(audit.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                    <div className="font-mono text-[10px] mb-1">
                      <span className="text-gray-500">DECISION: </span>
                      <span className={isBlock ? 'text-rp-red' : isOk ? 'text-rp-green' : 'text-gray-300'}>
                        {audit.decision}
                      </span>
                    </div>
                    {audit.input_summary && (
                      <div className="font-mono text-[9px] text-gray-500 mb-1 truncate">{audit.input_summary}</div>
                    )}
                    {Array.isArray(audit.reason_codes) && audit.reason_codes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {audit.reason_codes.map(c => (
                          <span key={c} className="text-[8px] font-mono bg-[#0a0a0b] border border-[#2a2a35] px-1.5 py-0.5 rounded text-gray-400">{c}</span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
