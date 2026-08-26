import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getBatches } from '../services/api';
import { Search, Activity, RefreshCw } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

const STATUS_COLORS = {
  APPROVED:                       'text-rp-cyan border-rp-cyan',
  BLOCKED:                        'text-rp-red border-rp-red',
  RECOVERY_VERIFIED:              'text-rp-green border-rp-green',
  EXECUTION_SUCCEEDED:            'text-rp-green border-rp-green',
  POLICY_BLOCKED:                 'text-rp-red border-rp-red',
  NO_ACTION_REQUIRED:             'text-rp-amber border-rp-amber',
  MERCHANT_ESCALATION_REQUIRED:   'text-rp-amber border-rp-amber',
  PENDING:                        'text-rp-amber border-rp-amber',
  ERROR:                          'text-rp-red border-rp-red bg-rp-red/10',
  FAILED:                         'text-rp-red border-rp-red border-dashed',
};

const StatusBadge = ({ status }) => {
  const color = STATUS_COLORS[status] || 'text-gray-400 border-gray-600';
  return (
    <span className={clsx('px-2 py-0.5 rounded text-[9px] font-bold font-mono border whitespace-nowrap', color)}>
      {status}
    </span>
  );
};

export default function BatchOperations() {
  const [batches, setBatches]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [query, setQuery]       = useState('');
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    getBatches()
      .then(setBatches)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const filtered = batches.filter(b =>
    !query ||
    b.payment_id?.toLowerCase().includes(query.toLowerCase()) ||
    b.workflow_status?.toLowerCase().includes(query.toLowerCase()) ||
    b.failure_category?.toLowerCase().includes(query.toLowerCase()) ||
    b.recommended_action?.toLowerCase().includes(query.toLowerCase())
  );

  if (loading)
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <Activity className="text-rp-cyan animate-spin" size={32} />
          <span className="font-mono text-sm text-rp-cyan tracking-widest">LOADING BATCH DATA...</span>
        </div>
      </div>
    );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">BATCH OPERATIONS</h1>
          <p className="text-gray-400 text-sm font-mono tracking-wide">
            VIEW AND INVESTIGATE PROCESSED PAYMENTS — {batches.length} TOTAL RUNS
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search payment ID, status, action..."
              className="bg-[#121214] border border-[#1e1e24] rounded-md pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-rp-cyan transition-colors font-mono w-72"
            />
          </div>
          <button onClick={load} className="p-2 rounded border border-[#1e1e24] text-gray-400 hover:text-rp-cyan hover:border-rp-cyan transition-colors">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-[10px] uppercase bg-[#1a1a24] text-gray-400 font-mono tracking-wider">
              <tr>
                <th className="px-5 py-4">Payment ID</th>
                <th className="px-5 py-4">Amount</th>
                <th className="px-5 py-4">Failure Category</th>
                <th className="px-5 py-4">Rec. Prob.</th>
                <th className="px-5 py-4">Rec. Action</th>
                <th className="px-5 py-4">Policy</th>
                <th className="px-5 py-4">Recovered</th>
                <th className="px-5 py-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((batch, i) => (
                <motion.tr
                  key={batch.run_id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(i * 0.03, 0.5) }}
                  onClick={() => navigate(`/batches/${encodeURIComponent(batch.run_id)}`)}
                  className="border-b border-[#1e1e24] hover:bg-[#1a1a24] cursor-pointer transition-colors group"
                >
                  <td className="px-5 py-3 font-mono text-rp-cyan text-xs group-hover:text-white transition-colors">
                    {batch.payment_id}
                  </td>
                  <td className="px-5 py-3 text-white text-sm font-mono">
                    ₹{Number(batch.amount || 0).toLocaleString()}
                  </td>
                  <td className="px-5 py-3 text-gray-300 text-xs">
                    {batch.failure_category || '—'}
                  </td>
                  <td className="px-5 py-3 font-mono text-sm">
                    <span className={
                      batch.recovery_probability > 0.7 ? 'text-rp-green' :
                      batch.recovery_probability > 0.4 ? 'text-rp-amber' : 'text-rp-red'
                    }>
                      {batch.recovery_probability != null
                        ? `${(batch.recovery_probability * 100).toFixed(0)}%`
                        : '—'}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-300 text-xs font-mono">
                    {batch.recommended_action || '—'}
                  </td>
                  <td className="px-5 py-3">
                    <StatusBadge status={batch.policy_decision} />
                  </td>
                  <td className="px-5 py-3 font-mono text-sm">
                    {batch.recovered_amount > 0
                      ? <span className="text-rp-green font-bold">₹{Number(batch.recovered_amount).toLocaleString()}</span>
                      : <span className="text-gray-600">—</span>}
                  </td>
                  <td className="px-5 py-3">
                    <StatusBadge status={batch.workflow_status} />
                  </td>
                </motion.tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="8" className="px-6 py-10 text-center text-gray-500 font-mono text-xs">
                    {query ? `No records matching "${query}"` : 'NO RECORDS FOUND'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
