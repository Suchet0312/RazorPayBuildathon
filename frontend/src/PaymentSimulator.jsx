import { useState } from 'react';
import { CreditCard, Activity, Send } from 'lucide-react';
import { analyzePayment } from './services/api';

const FAILURE_REASONS = [
  'bank_timeout', 'network_error', 'gateway_timeout',
  'insufficient_funds', 'authentication_failed', 'card_expired',
  'cart_abandoned', 'session_expired', 'inactivity',
  'mandate_rejected', 'nach_bounce', 'subscription_failed',
  'b2b_overdue', 'invoice_overdue',
  'fraud_detected', 'closed_account', 'invalid_details',
];

const randId = () => `pay_${Math.floor(Math.random() * 100000)}`;

export default function PaymentSimulator({ onRunStarted }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    payment_id: randId(),
    customer_id: 'cust_example',
    merchant_id: 'merch_main',
    amount: 2500,         // keep under ₹10,000 policy limit for demos
    currency: 'INR',
    payment_method: 'card',
    status: 'failed',
    failure_reason: 'insufficient_funds',
    attempt_count: 0,     // 0 attempts → higher probability of approval
    customer_success_rate: 0.8,
    previous_retry_success_rate: 0.75,
    contact_count: 0,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['amount', 'attempt_count', 'contact_count',
                'customer_success_rate', 'previous_retry_success_rate'].includes(name)
        ? Number(value)
        : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...formData, event_timestamp: new Date().toISOString() };
      const data = await analyzePayment(payload);
      if (data?.run_id && onRunStarted) onRunStarted(data.run_id);
    } catch (err) {
      console.error('Error starting recovery:', err);
      alert('Failed to start workflow. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
      setFormData(prev => ({ ...prev, payment_id: randId() }));
    }
  };

  return (
    <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6 relative overflow-hidden group hover:border-rp-cyan transition-colors">
      <div className="absolute top-0 right-0 w-32 h-32 bg-rp-cyan opacity-5 blur-3xl group-hover:opacity-10 transition-opacity" />

      <div className="flex items-center gap-3 mb-6">
        <CreditCard size={20} className="text-rp-cyan" />
        <h3 className="text-gray-400 font-mono text-xs tracking-wider">RAZORPAY TEST GATEWAY (DUMMY)</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Payment ID</label>
            <input type="text" name="payment_id" value={formData.payment_id} onChange={handleChange}
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors" required />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">
              Amount (₹) <span className="text-rp-amber normal-case">max ₹10,000 for auto-recovery</span>
            </label>
            <input type="number" name="amount" value={formData.amount} onChange={handleChange}
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors" required />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Failure Reason</label>
            <select name="failure_reason" value={formData.failure_reason} onChange={handleChange}
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors">
              {FAILURE_REASONS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Payment Method</label>
            <select name="payment_method" value={formData.payment_method} onChange={handleChange}
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors">
              {['card', 'upi', 'netbanking', 'nach', 'neft', 'wallet'].map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Attempt Count</label>
            <input type="number" name="attempt_count" value={formData.attempt_count} onChange={handleChange} min="0" max="5"
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Customer Success Rate (0–1)</label>
            <input type="number" step="0.05" name="customer_success_rate" value={formData.customer_success_rate} onChange={handleChange} min="0" max="1"
              className="bg-[#1a1a24] border border-[#2a2a35] rounded p-2 text-xs font-mono text-white focus:outline-none focus:border-rp-cyan transition-colors" />
          </div>
        </div>

        <button type="submit" disabled={loading}
          className="w-full mt-4 bg-[#1a1a24] border border-rp-cyan text-rp-cyan hover:bg-rp-cyan hover:text-black font-bold font-mono tracking-widest text-xs py-3 rounded transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          {loading
            ? <><Activity className="animate-spin" size={16} /> PROCESSING...</>
            : <><Send size={16} /> TRIGGER RECOVERY PIPELINE</>}
        </button>
      </form>
    </div>
  );
}
