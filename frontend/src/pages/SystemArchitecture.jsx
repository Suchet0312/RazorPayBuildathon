import { Network } from 'lucide-react';
import { motion } from 'framer-motion';

const SystemArchitecture = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Network className="text-rp-cyan" />
          SYSTEM ARCHITECTURE
        </h1>
        <p className="text-gray-400 text-sm font-mono tracking-wide">
          BOUNDED AI AUTONOMY WORKFLOW
        </p>
      </div>

      <div className="bg-[#121214] border border-[#1e1e24] rounded-lg p-8 max-w-4xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-rp-magenta opacity-5 blur-3xl pointer-events-none" />
        
        <div className="space-y-8 relative z-10">
          
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="border border-[#1e1e24] rounded-lg p-6 bg-[#0a0a0b]/80 relative group hover:border-rp-magenta transition-colors">
            <h3 className="text-rp-magenta font-bold tracking-wider mb-4 font-mono text-sm">AI ZONE</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-magenta/50 transition-colors">Classification Engine</div>
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-magenta/50 transition-colors">ML Predictor</div>
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-magenta/50 transition-colors">Diagnosis Agent</div>
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-magenta/50 transition-colors">Recovery Planner</div>
            </div>
          </motion.div>

          <div className="flex justify-center">
            <div className="h-8 w-px bg-gradient-to-b from-rp-magenta to-rp-amber" />
          </div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="border border-rp-amber/30 rounded-lg p-6 bg-[#0a0a0b]/80 relative group hover:border-rp-amber transition-colors">
            <h3 className="text-rp-amber font-bold tracking-wider mb-4 font-mono text-sm">DETERMINISTIC CONTROL ZONE</h3>
            <div className="bg-[#1a1a24] p-4 rounded border border-rp-amber/50 text-center font-bold text-white tracking-widest relative overflow-hidden">
              <div className="absolute inset-0 bg-rp-amber/5 opacity-50" />
              POLICY GUARDIAN
              <p className="text-[10px] text-rp-amber font-mono mt-1 font-normal tracking-normal">AI CANNOT BYPASS POLICY</p>
            </div>
          </motion.div>

          <div className="flex justify-center">
            <div className="h-8 w-px bg-gradient-to-b from-rp-amber to-rp-cyan" />
          </div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="border border-[#1e1e24] rounded-lg p-6 bg-[#0a0a0b]/80 relative group hover:border-rp-cyan transition-colors">
            <h3 className="text-rp-cyan font-bold tracking-wider mb-4 font-mono text-sm">EXECUTION ZONE</h3>
            <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-cyan/50 transition-colors w-1/2 mx-auto">
              Razorpay Test Mode Integration
            </div>
          </motion.div>

          <div className="flex justify-center">
            <div className="h-8 w-px bg-gradient-to-b from-rp-cyan to-rp-green" />
          </div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.7 }} className="border border-[#1e1e24] rounded-lg p-6 bg-[#0a0a0b]/80 relative group hover:border-rp-green transition-colors">
            <h3 className="text-rp-green font-bold tracking-wider mb-4 font-mono text-sm">TRUTH / EVIDENCE ZONE</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-green/50 transition-colors">Verification</div>
              <div className="bg-[#1a1a24] p-3 rounded border border-[#2a2a35] text-center text-xs font-mono text-gray-300 group-hover:border-rp-green/50 transition-colors">Audit Trail</div>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
};

export default SystemArchitecture;
