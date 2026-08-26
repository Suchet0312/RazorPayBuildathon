import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, IndianRupee, Activity, CheckCircle, XCircle, AlertOctagon } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { getMetrics } from '../services/api';
import PaymentSimulator from '../PaymentSimulator';
import WorkflowTracker from '../WorkflowTracker';

const MetricCard = ({ title, value, icon: Icon, delay, color = 'cyan', subtitle }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className={`bg-[#121214] border border-[#1e1e24] rounded-lg p-6 relative overflow-hidden group hover:border-rp-${color} transition-colors`}
  >
    <div className={`absolute top-0 right-0 w-32 h-32 bg-rp-${color} opacity-5 blur-3xl group-hover:opacity-10 transition-opacity`} />
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-gray-400 font-mono text-xs tracking-wider">{title}</h3>
      <div className={`p-2 rounded-md bg-[#1a1a24] text-rp-${color}`}><Icon size={18} /></div>
    </div>
    <div className="flex items-baseline gap-2">
      <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
      {subtitle && <span className="text-sm text-gray-500 font-mono">{subtitle}</span>}
    </div>
  </motion.div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1a1a24] border border-[#2a2a35] rounded p-3 font-mono text-xs">
      <p className="text-gray-400 mb-1">{label}</p>
      <p className="text-rp-cyan font-bold">₹{payload[0]?.value?.toLocaleString()}</p>
    </div>
  );
};

const Overview = () => {
  const [metrics, setMetrics]   = useState(null);
  const [loading, setLoading]   = useState(true);
  const [activeRunId, setActiveRunId] = useState(null);

  const refresh = () => getMetrics().then(setMetrics).catch(console.error);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  const chartData = metrics
    ? [
        { name: 'AT RISK',      value: metrics.revenue_at_risk },
        { name: 'PREDICTED',    value: metrics.predicted_recoverable },
        { name: 'RECOVERED',    value: metrics.actually_recovered },
      ]
    : [];

  const CHART_COLORS = ['#F0B90B', '#0DF5E3', '#00D09C'];

  if (loading)
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <Activity className="text-rp-cyan animate-spin" size={32} />
          <span className="font-mono text-sm text-rp-cyan tracking-widest">INITIALIZING SECURE LINK...</span>
        </div>
      </div>
    );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">COMMAND CENTER</h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">AI-POWERED REVENUE RECOVERY DASHBOARD</p>
      </div>

      {/* Row 1 – primary revenue metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard title="REVENUE AT RISK"       value={`₹${metrics?.revenue_at_risk?.toLocaleString() ?? 0}`}       icon={ShieldAlert}  delay={0.1} color="amber" />
        <MetricCard title="PREDICTED RECOVERABLE" value={`₹${metrics?.predicted_recoverable?.toLocaleString() ?? 0}`} icon={Activity}     delay={0.2} color="cyan" />
        <MetricCard title="ACTUALLY RECOVERED"    value={`₹${metrics?.actually_recovered?.toLocaleString() ?? 0}`}    icon={IndianRupee}  delay={0.3} color="green" />
        <MetricCard title="RECOVERY RATE"         value={`${metrics?.recovery_rate?.toFixed(1) ?? 0}%`}               icon={CheckCircle}  delay={0.4} color="magenta" />
      </div>

      {/* Row 2 – policy counters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="ACTIONS APPROVED"       value={metrics?.actions_approved ?? 0}      icon={CheckCircle}  delay={0.5} color="cyan"  subtitle="Policy Guardian" />
        <MetricCard title="ACTIONS BLOCKED"        value={metrics?.actions_blocked ?? 0}       icon={XCircle}      delay={0.6} color="red"   subtitle="Policy Guardian" />
        <MetricCard title="UNRESOLVED EXCEPTIONS"  value={metrics?.unresolved_exceptions ?? 0} icon={AlertOctagon} delay={0.7} color="amber" subtitle="Workflow Failures" />
      </div>

      {/* Row 3 – simulator + tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PaymentSimulator onRunStarted={(runId) => {
          setActiveRunId(runId);
          setTimeout(refresh, 4000); // refresh metrics after workflow completes
        }} />
        <WorkflowTracker runId={activeRunId} />
      </div>

      {/* Row 4 – recovery funnel chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.9 }}
        className="bg-[#121214] border border-[#1e1e24] rounded-lg p-6"
      >
        <h3 className="text-gray-400 font-mono text-xs tracking-wider mb-6">RECOVERY FUNNEL — REVENUE (₹)</h3>
        {chartData.length > 0 && chartData[0].value > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} barCategoryGap="35%">
              <XAxis dataKey="name" tick={{ fill: '#6B7280', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[200px] items-center justify-center border border-dashed border-[#1e1e24] rounded">
            <span className="text-gray-600 font-mono text-sm">No payment data yet — submit a payment above to populate the chart</span>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Overview;
