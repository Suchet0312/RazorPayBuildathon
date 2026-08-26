import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, GitBranch, ShieldCheck, ShieldX } from 'lucide-react';
import { getRunStatus } from './services/api';

const STAGE_LABELS = {
  classification:  'CLASSIFICATION',
  prediction:      'ML PREDICTION',
  diagnosis:       'DIAGNOSIS',
  planning:        'PLANNING',
  policy_gate:     'POLICY GATE',
  execution:       'EXECUTION',
  verification:    'VERIFICATION',
};

const STATUS_COLOR = {
  RECOVERY_VERIFIED:              'text-rp-green',
  EXECUTION_SUCCEEDED:            'text-rp-green',
  POLICY_BLOCKED:                 'text-rp-red',
  NO_ACTION_REQUIRED:             'text-rp-amber',
  MERCHANT_ESCALATION_REQUIRED:   'text-rp-amber',
  EXECUTION_FAILED:               'text-rp-red',
  RECOVERY_NOT_VERIFIED:          'text-rp-red',
  PENDING:                        'text-rp-cyan animate-pulse',
  ERROR:                          'text-rp-red',
};

function StageIcon({ result }) {
  if (result === 'success' || result === 'classified' || result === 'plan_selected' || result === 'approved' || result === 'probability_computed' || result === 'diagnosis_complete')
    return <CheckCircle size={14} className="text-rp-green" />;
  if (result === 'failed' || result === 'blocked')
    return <XCircle size={14} className="text-rp-red" />;
  return <AlertTriangle size={14} className="text-rp-amber" />;
}

export default function WorkflowTracker({ runId }) {
  const [status, setStatus] = useState(null);
  const [error, setError]   = useState(null);

  useEffect(() => {
    if (!runId) return;

    let cancelled = false;
    const poll = async () => {
      try {
        const data = await getRunStatus(runId);
        if (!cancelled) {
          setStatus(data);
          // Stop polling once the workflow has reached a terminal state
          if (data.workflow_status && data.workflow_status !== 'PENDING') {
            clearInterval(intervalId);
          }
        }
      } catch {
        if (!cancelled) setError('Error fetching workflow status.');
      }
    };

    poll();
    const intervalId = setInterval(poll, 1500);
    return () => { cancelled = true; clearInterval(intervalId); };
  }, [runId]);

  if (!runId)
    return (
      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-8 flex flex-col items-center justify-center min-h-[320px] text-gray-500">
        <GitBranch size={40} className="mb-4 opacity-30" />
        <p className="font-mono text-xs text-center leading-relaxed">
          No active workflow.<br />Submit a payment above to track its recovery journey.
        </p>
      </div>
    );

  if (error)
    return (
      <div className="bg-[#121214] border border-rp-red rounded-lg p-6 text-rp-red font-mono text-xs">{error}</div>
    );

  if (!status)
    return (
      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-8 flex items-center justify-center gap-3 min-h-[320px]">
        <Activity className="animate-spin text-rp-cyan" size={20} />
        <span className="font-mono text-sm text-rp-cyan tracking-widest">LOADING WORKFLOW STATUS...</span>
      </div>
    );

  const statusColor = STATUS_COLOR[status.workflow_status] || 'text-gray-400';

  return (
    <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="font-mono text-xs text-gray-400 tracking-wider mb-1">LIVE WORKFLOW TRACKER</h3>
          <span className="font-mono text-[10px] text-gray-600">{runId}</span>
        </div>
        <span className={`font-mono text-xs font-bold border px-3 py-1 rounded ${statusColor} border-current`}>
          {status.workflow_status}
        </span>
      </div>

      {/* Audit timeline */}
      <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
        {(status.audit_trail || []).map((audit, i) => (
          <div key={i} className="flex gap-3 items-start">
            <div className="mt-0.5 shrink-0"><StageIcon result={audit.result} /></div>
            <div className="flex-1 bg-[#1a1a24] border border-[#2a2a35] rounded p-3">
              <div className="flex justify-between items-center mb-1">
                <span className="font-mono text-[10px] text-rp-cyan font-bold tracking-wider">
                  {STAGE_LABELS[audit.stage] || audit.stage?.toUpperCase()}
                </span>
                <span className="font-mono text-[9px] text-gray-600">
                  {audit.timestamp ? new Date(audit.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
              <div className="font-mono text-[10px] text-gray-300 mb-1">
                <span className="text-gray-500">DECISION: </span>{audit.decision}
              </div>
              {audit.reason_codes?.length > 0 && (
                <div className="font-mono text-[9px] text-gray-500">
                  {audit.reason_codes.join(' · ')}
                </div>
              )}
            </div>
          </div>
        ))}

        {status.workflow_status === 'PENDING' && (
          <div className="flex gap-3 items-center">
            <Activity size={14} className="animate-pulse text-rp-cyan shrink-0" />
            <span className="font-mono text-[10px] text-gray-500">Processing next node...</span>
          </div>
        )}
      </div>

      {status.recovered_amount > 0 && (
        <div className="mt-4 pt-4 border-t border-[#1e1e24] flex justify-between items-center font-mono text-xs">
          <span className="text-gray-400">RECOVERED AMOUNT</span>
          <span className="text-rp-green font-bold text-sm">₹{status.recovered_amount?.toLocaleString()}</span>
        </div>
      )}
    </div>
  );
}
