import { useState } from 'react';
import { motion } from 'framer-motion';
import { Layers, Play, CheckCircle, XCircle, Activity, IndianRupee } from 'lucide-react';
import { analyzeBatch } from '../services/api';

const FAILURE_SCENARIOS = [
  // High-probability temp failures → RECOVERY_VERIFIED
  { failure_reason: 'bank_timeout',        payment_method: 'upi',  amount: 1500, csr: 0.85, prsr: 0.80, label: 'Bank Timeout (Temp)',    desc: '₹1,500 · upi' },
  { failure_reason: 'network_error',       payment_method: 'card', amount: 2000, csr: 0.80, prsr: 0.75, label: 'Network Error (Temp)',   desc: '₹2,000 · card' },
  { failure_reason: 'gateway_timeout',     payment_method: 'upi',  amount: 3500, csr: 0.82, prsr: 0.78, label: 'Gateway Timeout',        desc: '₹3,500 · upi' },
  // These get POLICY_BLOCKED (ML prob < 0.55) — illustrates stopping rules
  { failure_reason: 'cart_abandoned',      payment_method: 'card', amount: 1800, csr: 0.80, prsr: 0.75, label: 'Cart Abandoned',         desc: '₹1,800 · card' },
  { failure_reason: 'insufficient_funds',  payment_method: 'card', amount: 5200, csr: 0.80, prsr: 0.75, label: 'Insufficient Funds',     desc: '₹5,200 · card' },
  { failure_reason: 'subscription_failed', payment_method: 'nach', amount: 599,  csr: 0.80, prsr: 0.75, label: 'Subscription Failed',    desc: '₹599 · nach' },
  // Permanent failure — always DO_NOTHING
  { failure_reason: 'fraud_detected',      payment_method: 'card', amount: 4000, csr: 0.50, prsr: 0.50, label: 'Fraud Detected (Perm)', desc: '₹4,000 · card' },
  // Session expired — checkout abandonment
  { failure_reason: 'session_expired',     payment_method: 'upi',  amount: 450,  csr: 0.80, prsr: 0.75, label: 'Session Expired',        desc: '₹450 · upi' },
];

const STATUS_COLORS = {
  RECOVERY_VERIFIED:            'text-rp-green border-rp-green',
  EXECUTION_SUCCEEDED:          'text-rp-green border-rp-green',
  POLICY_BLOCKED:               'text-rp-red border-rp-red',
  NO_ACTION_REQUIRED:           'text-rp-amber border-rp-amber',
  MERCHANT_ESCALATION_REQUIRED: 'text-rp-amber border-rp-amber',
  ERROR:                        'text-rp-red border-rp-red',
  PENDING:                      'text-rp-cyan border-rp-cyan',
};

function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || 'text-gray-400 border-gray-600';
  return (
    <span className={`px-2 py-0.5 rounded text-[9px] font-bold font-mono border ${color}`}>{status}</span>
  );
}

export default function BatchSubmit() {
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [selected, setSelected] = useState(new Set(FAILURE_SCENARIOS.map((_, i) => i)));

  const toggle = (i) => setSelected(prev => {
    const next = new Set(prev);
    next.has(i) ? next.delete(i) : next.add(i);
    return next;
  });

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payments = [...selected].map(i => {
        const s = FAILURE_SCENARIOS[i];
        return {
          payment_id:                  `batch_${Date.now()}_${i}`,
          customer_id:                 'cust_batch_demo',
          merchant_id:                 'merch_batch_demo',
          amount:                      s.amount,
          currency:                    'INR',
          payment_method:              s.payment_method,
          status:                      'failed',
          failure_reason:              s.failure_reason,
          attempt_count:               0,
          event_timestamp:             new Date().toISOString(),
          customer_success_rate:       s.csr  ?? 0.80,
          previous_retry_success_rate: s.prsr ?? 0.75,
          contact_count:               0,
        };
      });
      const data = await analyzeBatch({ payments, stop_on_error: false });
      setResult(data);
    } catch (err) {
      setError('Batch failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Layers className="text-rp-cyan" /> BATCH RECOVERY
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          RUN MULTIPLE PAYMENTS THROUGH THE RECOVERY PIPELINE IN ONE CALL — MEASURED MONEY RECOVERED ACROSS A BATCH
        </p>
      </div>

      {/* Scenario selector */}
      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
        <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-4">SELECT FAILURE SCENARIOS</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {FAILURE_SCENARIOS.map((s, i) => (
            <button key={i} onClick={() => toggle(i)}
              className={`p-3 rounded border text-left transition-colors ${selected.has(i)
                ? 'border-rp-cyan bg-rp-cyan/5 text-white'
                : 'border-[#2a2a35] text-gray-500 hover:border-gray-400'}`}>
              <div className="font-mono text-[10px] font-bold mb-1">{s.label}</div>
              <div className="font-mono text-[9px] text-gray-500">{s.desc}</div>
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <span className="font-mono text-xs text-gray-500">{selected.size} payments selected</span>
          <button onClick={handleRun} disabled={loading || selected.size === 0}
            className="bg-[#1a1a24] border border-rp-cyan text-rp-cyan hover:bg-rp-cyan hover:text-black font-bold font-mono tracking-widest text-xs py-2 px-6 rounded transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? <><Activity className="animate-spin" size={14} /> PROCESSING...</> : <><Play size={14} /> RUN BATCH</>}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rp-red/10 border border-rp-red text-rp-red rounded p-4 font-mono text-xs">{error}</div>
      )}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Aggregate metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'TOTAL PAYMENTS',     value: result.total,                                        icon: Layers,       color: 'cyan'   },
              { label: 'REVENUE AT RISK',    value: `₹${result.total_revenue_at_risk?.toLocaleString()}`, icon: IndianRupee,  color: 'amber'  },
              { label: 'PREDICTED RECOVERY', value: `₹${result.total_predicted_recoverable?.toLocaleString()}`, icon: Activity, color: 'cyan' },
              { label: 'ACTUALLY RECOVERED', value: `₹${result.total_actually_recovered?.toLocaleString()}`,    icon: CheckCircle, color: 'green' },
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className={`bg-[#121214] border border-[#1e1e24] rounded-lg p-4 hover:border-rp-${color} transition-colors`}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-mono text-[9px] text-gray-400 tracking-wider">{label}</span>
                  <Icon size={14} className={`text-rp-${color}`} />
                </div>
                <span className="text-xl font-bold text-white">{value}</span>
              </div>
            ))}
          </div>

          {/* Per-payment results table */}
          <div className="bg-[#121214] border border-[#1e1e24] rounded-lg overflow-hidden">
            <div className="px-6 py-3 border-b border-[#1e1e24] font-mono text-xs text-gray-400 tracking-wider">
              PER-PAYMENT RESULTS — {result.total} processed · {result.succeeded} completed · {result.failed} errored
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-[#1a1a24] text-[10px] font-mono text-gray-500 tracking-wider">
                  <tr>
                    <th className="px-4 py-3 text-left">PAYMENT_ID</th>
                    <th className="px-4 py-3 text-left">ACTION</th>
                    <th className="px-4 py-3 text-left">PROB</th>
                    <th className="px-4 py-3 text-left">POLICY</th>
                    <th className="px-4 py-3 text-left">RECOVERED</th>
                    <th className="px-4 py-3 text-left">STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {result.results.map((r, i) => (
                    <tr key={i} className="border-b border-[#1e1e24] hover:bg-[#1a1a24] transition-colors">
                      <td className="px-4 py-3 font-mono text-rp-cyan">{r.payment_id?.split('_').slice(-2).join('_')}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{r.recommended_action || '—'}</td>
                      <td className="px-4 py-3 font-mono">
                        <span className={r.recovery_probability > 0.7 ? 'text-rp-green' : r.recovery_probability > 0.4 ? 'text-rp-amber' : 'text-rp-red'}>
                          {r.recovery_probability != null ? `${(r.recovery_probability * 100).toFixed(0)}%` : '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {r.policy_approved === true  && <span className="text-rp-green font-mono text-[9px]">APPROVED</span>}
                        {r.policy_approved === false && <span className="text-rp-red font-mono text-[9px]">BLOCKED</span>}
                        {r.policy_approved == null  && <span className="text-gray-500 font-mono text-[9px]">—</span>}
                      </td>
                      <td className="px-4 py-3 font-mono text-rp-green">
                        {r.recovered_amount > 0 ? `₹${r.recovered_amount?.toLocaleString()}` : '—'}
                      </td>
                      <td className="px-4 py-3"><StatusBadge status={r.workflow_status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
