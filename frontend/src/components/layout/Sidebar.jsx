import { NavLink } from 'react-router-dom';
import { useEffect, useState } from 'react';
import {
  LayoutDashboard, List, Activity, Network, AlertTriangle,
  TerminalSquare, Layers, Handshake, Mic,
} from 'lucide-react';
import clsx from 'clsx';
import { getHealth } from '../../services/api';

const navItems = [
  { to: '/',             icon: LayoutDashboard, label: 'OVERVIEW'            },
  { to: '/batches',      icon: List,            label: 'BATCH OPERATIONS'    },
  { to: '/batch-submit', icon: Layers,          label: 'BATCH RECOVERY'      },
  { to: '/promise-pay',  icon: Handshake,       label: 'PROMISE TO PAY'      },
  { to: '/hinglish',     icon: Mic,             label: 'HINGLISH RECOVERY'   },
  { to: '/failure-lab',  icon: AlertTriangle,   label: 'FAILURE LAB'         },
  { to: '/architecture', icon: Network,         label: 'SYSTEM ARCHITECTURE' },
];

export default function Sidebar() {
  const [apiUp, setApiUp] = useState(null); // null=checking, true=up, false=down

  useEffect(() => {
    const check = async () => {
      try {
        await getHealth();
        setApiUp(true);
      } catch {
        setApiUp(false);
      }
    };
    check();
    const id = setInterval(check, 15_000); // re-check every 15 s
    return () => clearInterval(id);
  }, []);

  const dot = apiUp === null
    ? 'bg-rp-amber animate-pulse'
    : apiUp
    ? 'bg-rp-green glow-green'
    : 'bg-rp-red';

  return (
    <div className="w-64 border-r border-[#1e1e24] bg-bg-panel h-screen flex flex-col text-sm">
      {/* Logo */}
      <div className="p-6 border-b border-[#1e1e24]">
        <div className="flex items-center gap-3">
          <TerminalSquare className="text-rp-cyan" size={24} />
          <div>
            <h1 className="font-bold text-white tracking-wider">RAZORPAY</h1>
            <p className="text-xs text-rp-cyan tracking-widest font-mono mt-1">RECOVERY_BRAIN</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-3 flex flex-col gap-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-4 py-2.5 rounded-md transition-all duration-200 font-mono text-xs tracking-wider',
              isActive
                ? 'bg-[#1a1a24] text-rp-cyan border-l-2 border-rp-cyan glow-cyan'
                : 'text-gray-400 hover:text-white hover:bg-bg-panel-hover',
            )}
          >
            <item.icon size={15} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Status footer */}
      <div className="p-4 border-t border-[#1e1e24]">
        <div className="bg-[#121214] p-3 rounded-lg border border-[#1e1e24]">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-400 font-mono">SYSTEM STATUS</span>
            <div className={`w-2 h-2 rounded-full ${dot}`} />
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-400 font-mono">API HEALTH</span>
            <span className={`text-[10px] font-mono font-bold ${apiUp ? 'text-rp-green' : apiUp === false ? 'text-rp-red' : 'text-rp-amber'}`}>
              {apiUp === null ? 'CHECKING' : apiUp ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400 font-mono">RAZORPAY TEST MODE</span>
            <span className="text-[10px] bg-rp-cyan text-black px-2 py-0.5 rounded font-bold">ACTIVE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
