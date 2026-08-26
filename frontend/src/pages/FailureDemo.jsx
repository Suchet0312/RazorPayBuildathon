import { useState } from 'react';
import { simulateFailureDemo } from '../services/api';
import { AlertTriangle, ShieldAlert, CheckCircle, XCircle, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const STAGE_COLOR = {
  APPROVED:   'text-rp-green',
  SUCCESS:    'text-rp-green',
  PROCEED:    'text-rp-cyan',
  BLOCKED:    'text-rp-red',
  FAILED:     'text-rp-red',
};

export default function FailureDemo() {
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await simulateFailureDemo();
      setResult(data);
    } catch (err) {
      setError('Failed to reach API. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <AlertTriangle className="text-rp-amber" /> FAILURE LAB
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          CONTROLLED GRACEFUL FAILURE DEMONSTRATION — REAL WORKFLOW EXECUTION
        </p>
      </div>

      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6 max-w-3xl">
        <h3 className="text-lg font-bold text-white mb-3">Simulate Bank Timeout Scenario</h3>
        <p className="text-sm text-gray-400 mb-6 leading-relaxed">
          Injects a <span className="text-rp-amber font-mono">bank_timeout</span> failure on a ₹2,500 netbanking payment.
          The full LangGraph pipeline runs in real-time: classification → ML prediction → diagnosis →
          recovery plan → policy gate → execution → verification. The audit trail below shows each decision.
        </p>

        <button onClick={handleSimulate} disabled={loading}
          className="bg-rp-red/10 hover:bg-rp-red/20 border border-rp-red text-rp-red font-bold py-2 px-6 rounded transition-colors disabled:opacity-50 flex items-center gap-2">
          {loading
            ? <><Activity className="animate-spin" size={18} /> RUNNING PIPELINE...</>
            : <><ShieldAlert size={18} /> TRIGGER FAILURE SIMULATION</>}
        </button>

        {error && (
          <div className="mt-6 p-4 bg-rp-red/10 border border-rp-red text-rp-red rounded flex items-center gap-3 font-mono text-xs">
            <XCircle /> {error}
          </div>
        )}

        {result && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
            className="mt-8 border-t border-[#1e1e24] pt-6">
            <div className="flex items-center gap-3 mb-6">
              <CheckCircle className="text-rp-green" size={20} />
              <h4 className="text-white font-bold">Workflow Completed — Failure Contained</h4>
            </div>

            <div className="bg-[#0a0a0b] border border-[#1e1e24] rounded p-5 font-mono text-xs space-y-2 mb-6">
              <div><span className="text-gray-500">RUN_ID:</span>     <span className="text-rp-cyan ml-2">{result.run_id}</span></div>
              <div><span className="text-gray-500">STATUS:</span>     <span className={`ml-2 font-bold ${result.status?.includes('VERIFIED') ? 'text-rp-green' : result.status?.includes('BLOCKED') ? 'text-rp-red' : 'text-rp-amber'}`}>{result.status}</span></div>
              <div><span className="text-gray-500">MESSAGE:</span>    <span className="text-gray-300 ml-2">{result.message}</span></div>
            </div>

            <div className="text-gray-500 font-mono text-[10px] tracking-wider mb-3">AUDIT_TRAIL_DUMP</div>
            <div className="space-y-2">
              {result.audit_trail?.map((audit, i) => (
                <div key={i} className="flex gap-3 border-l-2 border-[#1e1e24] pl-3 py-1.5 hover:border-rp-cyan transition-colors">
                  <span className="text-gray-600 w-20 shrink-0 text-[10px]">
                    {audit.timestamp ? new Date(audit.timestamp).toLocaleTimeString() : ''}
                  </span>
                  <span className="text-rp-cyan w-32 shrink-0 text-[10px]">{audit.stage}</span>
                  <span className={`text-[10px] ${STAGE_COLOR[audit.decision?.toUpperCase()] || 'text-gray-300'}`}>
                    {audit.decision} — {audit.result}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
