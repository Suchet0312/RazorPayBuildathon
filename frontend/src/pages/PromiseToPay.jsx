import { useState } from 'react';
import { motion } from 'framer-motion';
import { Handshake, CheckCircle, XCircle, Calendar, Clock } from 'lucide-react';
import { recordPromiseToPay } from '../services/api';

export default function PromiseToPay() {
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [form, setForm]         = useState({
    payment_id:              `ptp_${Math.floor(Math.random() * 100000)}`,
    customer_id:             'cust_demo',
    merchant_id:             'merch_demo',
    amount:                  2500,
    currency:                'INR',
    commitment_window_days:  3,
    follow_up_enabled:       true,
    notes:                   '',
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked
               : ['amount', 'commitment_window_days'].includes(name) ? Number(value)
               : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await recordPromiseToPay(form);
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
          <Handshake className="text-rp-green" /> PROMISE-TO-PAY TRACKER
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          CAPTURE CUSTOMER PAYMENT COMMITMENTS AND SCHEDULE AUTOMATED FOLLOW-UPS
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6">
          <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-6">RECORD COMMITMENT</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {[
                { name: 'payment_id',  label: 'Payment ID',   type: 'text'   },
                { name: 'customer_id', label: 'Customer ID',  type: 'text'   },
                { name: 'merchant_id', label: 'Merchant ID',  type: 'text'   },
                { name: 'amount',      label: 'Amount (₹)',   type: 'number' },
              ].map(f => (
                <div key={f.name} className="flex flex-col gap-1">
                  <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">{f.label}</label>
                  <input type={f.type} name={f.name} value={form[f.name]} onChange={handleChange}
                    className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-green transition-colors" required />
                </div>
              ))}
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Commitment Window (days)</label>
              <input type="range" name="commitment_window_days" min="1" max="30" value={form.commitment_window_days} onChange={handleChange}
                className="accent-rp-green" />
              <div className="flex justify-between font-mono text-[10px] text-gray-500"><span>1 day</span><span className="text-rp-green font-bold">{form.commitment_window_days} days</span><span>30 days</span></div>
            </div>

            <div className="flex items-center gap-3">
              <input type="checkbox" name="follow_up_enabled" checked={form.follow_up_enabled} onChange={handleChange}
                className="accent-rp-green w-4 h-4" id="followup" />
              <label htmlFor="followup" className="text-xs text-gray-300 font-mono">Enable automated follow-up nudges</label>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Notes (optional)</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} rows={2}
                placeholder="Customer called in, promised to pay by Friday..."
                className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-green transition-colors resize-none" />
            </div>

            <button type="submit" disabled={loading}
              className="w-full bg-[#1a1a24] border border-rp-green text-rp-green hover:bg-rp-green hover:text-black font-bold font-mono tracking-widest text-xs py-3 rounded transition-all flex items-center justify-center gap-2 disabled:opacity-50">
              {loading ? '⏳ RECORDING...' : '✓ RECORD COMMITMENT'}
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
              className="bg-[#0a0a0b] border border-rp-green/40 rounded-lg p-6 space-y-4">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="text-rp-green" size={20} />
                <h3 className="text-rp-green font-bold font-mono tracking-wider">COMMITMENT RECORDED</h3>
              </div>

              <div className="space-y-3 font-mono text-sm">
                {[
                  ['REFERENCE_ID',  result.reference_id],
                  ['PAYMENT_ID',    result.payment_id],
                  ['CUSTOMER_ID',   result.customer_id],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between border-b border-[#1e1e24] pb-2">
                    <span className="text-gray-500 text-xs">{k}</span>
                    <span className="text-rp-cyan text-xs">{v}</span>
                  </div>
                ))}

                <div className="flex items-center gap-2 text-rp-amber">
                  <Calendar size={14} />
                  <span className="text-xs font-bold">DEADLINE: {result.commitment_deadline?.split('T')[0]}</span>
                </div>

                {result.follow_up_times?.length > 0 && (
                  <div>
                    <div className="text-gray-500 text-xs mb-2 flex items-center gap-2">
                      <Clock size={12} /> FOLLOW-UP SCHEDULE
                    </div>
                    {result.follow_up_times.map((t, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs text-gray-300 mb-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-rp-cyan" />
                        Follow-up {i + 1}: {new Date(t).toLocaleString()}
                      </div>
                    ))}
                  </div>
                )}

                <div className="bg-[#1a1a24] border border-[#2a2a35] rounded p-3 text-xs text-gray-300 leading-relaxed">
                  {result.message}
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="bg-[#121214] border border-dashed border-[#2a2a35] rounded-lg p-8 flex flex-col items-center justify-center min-h-[300px] text-gray-600">
              <Handshake size={40} className="mb-4 opacity-20" />
              <p className="font-mono text-xs text-center">Submit the form to capture a promise-to-pay commitment and see the follow-up schedule here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
