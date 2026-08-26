import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mic, Send, MessageSquare, CheckCircle, XCircle } from 'lucide-react';
import { sendHinglishRecovery } from '../services/api';

const CHANNELS  = ['sms', 'voice', 'whatsapp'];
const SCENARIOS = [
  { label: 'Insufficient Funds',   failure_reason: 'insufficient_funds',  amount: 1200 },
  { label: 'Authentication Failed',failure_reason: 'authentication_failed',amount: 3500 },
  { label: 'Mandate Rejected',     failure_reason: 'mandate_rejected',     amount: 999  },
  { label: 'Cart Abandoned',       failure_reason: 'cart_abandoned',       amount: 450  },
  { label: 'Generic Failure',      failure_reason: 'bank_timeout',         amount: 2000 },
];

export default function HinglishRecovery() {
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [error, setError]     = useState(null);
  const [form, setForm]       = useState({
    payment_id:     `h_${Math.floor(Math.random() * 100000)}`,
    customer_id:    'cust_hinglish',
    merchant_id:    'merch_demo',
    amount:         1200,
    currency:       'INR',
    failure_reason: 'insufficient_funds',
    channel:        'sms',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'amount' ? Number(value) : value }));
  };

  const applyScenario = (s) => {
    setForm(prev => ({ ...prev, failure_reason: s.failure_reason, amount: s.amount }));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await sendHinglishRecovery(form);
      setResult(data);
    } catch (err) {
      setError('Failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Mic className="text-rp-magenta" /> HINGLISH VOICE RECOVERY
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          DISPATCH HINDI + ENGLISH (HINGLISH) RECOVERY NUDGES VIA SMS · VOICE · WHATSAPP
        </p>
      </div>

      {/* Scenario quick-picks */}
      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-4">
        <div className="font-mono text-[10px] text-gray-500 tracking-wider mb-3">QUICK SCENARIOS</div>
        <div className="flex flex-wrap gap-2">
          {SCENARIOS.map(s => (
            <button key={s.failure_reason} onClick={() => applyScenario(s)}
              className={`px-3 py-1.5 rounded border font-mono text-[10px] transition-colors ${
                form.failure_reason === s.failure_reason
                  ? 'border-rp-magenta text-rp-magenta bg-rp-magenta/5'
                  : 'border-[#2a2a35] text-gray-500 hover:border-gray-400'}`}>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
          <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-6">CONFIGURE MESSAGE</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Payment ID</label>
                <input type="text" name="payment_id" value={form.payment_id} onChange={handleChange}
                  className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-magenta transition-colors" required />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Amount (₹)</label>
                <input type="number" name="amount" value={form.amount} onChange={handleChange}
                  className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-magenta transition-colors" required />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Customer ID</label>
                <input type="text" name="customer_id" value={form.customer_id} onChange={handleChange}
                  className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-magenta transition-colors" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Failure Reason</label>
                <input type="text" name="failure_reason" value={form.failure_reason} onChange={handleChange}
                  className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-magenta transition-colors" />
              </div>
            </div>

            {/* Channel selector */}
            <div>
              <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-2">Delivery Channel</div>
              <div className="flex gap-3">
                {CHANNELS.map(c => (
                  <button key={c} type="button" onClick={() => setForm(p => ({ ...p, channel: c }))}
                    className={`flex-1 py-2 rounded border font-mono text-xs font-bold transition-colors ${
                      form.channel === c
                        ? 'border-rp-magenta text-rp-magenta bg-rp-magenta/5'
                        : 'border-[#2a2a35] text-gray-500 hover:border-gray-400'}`}>
                    {c.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full bg-[#1a1a24] border border-rp-magenta text-rp-magenta hover:bg-rp-magenta hover:text-black font-bold font-mono tracking-widest text-xs py-3 rounded transition-all flex items-center justify-center gap-2 disabled:opacity-50">
              {loading ? '⏳ DISPATCHING...' : <><Send size={14} /> DISPATCH HINGLISH MESSAGE</>}
            </button>
          </form>

          {error && (
            <div className="mt-4 flex items-center gap-2 text-rp-red text-xs font-mono">
              <XCircle size={14} /> {error}
            </div>
          )}
        </div>

        {/* Result */}
        <div>
          {result ? (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              className="bg-[#0a0a0b] border border-rp-magenta/40 rounded-lg p-6 space-y-4">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle className="text-rp-green" size={20} />
                <h3 className="text-white font-bold font-mono">MESSAGE DISPATCHED</h3>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between border-b border-[#1e1e24] pb-2">
                  <span className="text-gray-500">REFERENCE_ID</span>
                  <span className="text-rp-cyan">{result.reference_id}</span>
                </div>
                <div className="flex justify-between border-b border-[#1e1e24] pb-2">
                  <span className="text-gray-500">CHANNEL</span>
                  <span className="text-rp-magenta font-bold uppercase">{result.channel}</span>
                </div>
                <div className="flex justify-between border-b border-[#1e1e24] pb-2">
                  <span className="text-gray-500">DISPATCHED_AT</span>
                  <span className="text-gray-300">{result.dispatched_at ? new Date(result.dispatched_at).toLocaleString() : '—'}</span>
                </div>
              </div>

              {result.message_sent && (
                <div>
                  <div className="flex items-center gap-2 text-gray-500 text-[10px] font-mono tracking-wider mb-2">
                    <MessageSquare size={12} /> HINGLISH MESSAGE
                  </div>
                  <div className="bg-[#1a1a24] border border-rp-magenta/20 rounded p-4 text-sm text-white leading-relaxed font-sans">
                    {result.message_sent}
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="bg-[#121214] border border-dashed border-[#2a2a35] rounded-lg p-8 flex flex-col items-center justify-center min-h-[300px] text-gray-600">
              <Mic size={40} className="mb-4 opacity-20" />
              <p className="font-mono text-xs text-center">Configure and dispatch a message to see the Hinglish recovery nudge here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
