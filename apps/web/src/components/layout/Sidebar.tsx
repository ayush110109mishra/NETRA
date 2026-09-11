import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Compass,
  Box,
  BrainCircuit,
  BellRing,
  Activity,
  FileText,
  LineChart,
  ShieldAlert,
  Settings,
} from 'lucide-react';
import { clsx } from 'clsx';
import { ROUTES } from '@netra/shared';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  badge?: string;
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    path: ROUTES.DASHBOARD,
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: 'Missions',
    path: ROUTES.MISSIONS,
    icon: <Compass className="w-4 h-4" />,
  },
  {
    label: 'Assets',
    path: ROUTES.ASSETS,
    icon: <Box className="w-4 h-4" />,
  },
  {
    label: 'Intelligence',
    path: ROUTES.INTELLIGENCE,
    icon: <BrainCircuit className="w-4 h-4" />,
  },
  {
    label: 'Alerts',
    path: ROUTES.ALERTS,
    icon: <BellRing className="w-4 h-4" />,
  },
  {
    label: 'Telemetry',
    path: ROUTES.TELEMETRY,
    icon: <Activity className="w-4 h-4" />,
  },
  {
    label: 'Documents',
    path: ROUTES.DOCUMENTS,
    icon: <FileText className="w-4 h-4" />,
  },
  {
    label: 'Analytics',
    path: ROUTES.ANALYTICS,
    icon: <LineChart className="w-4 h-4" />,
  },
  {
    label: 'Audit Logs',
    path: ROUTES.AUDIT_LOGS,
    icon: <ShieldAlert className="w-4 h-4" />,
  },
  {
    label: 'Settings',
    path: ROUTES.SETTINGS,
    icon: <Settings className="w-4 h-4" />,
  },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-60 bg-tactical-surface border-r border-slate-800 flex flex-col justify-between shrink-0 select-none">
      {/* Corporate Brand Header */}
      <div className="p-3 border-b border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-2.5">
          <img
            src="/assets/astraveda-logo.jpg"
            alt="Astraveda"
            className="w-8 h-8 rounded-xs border border-cyan-500/30 object-cover shadow-sm shrink-0"
          />
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-mono font-bold tracking-wider text-slate-100 uppercase truncate">
              ASTRAVEDA
            </span>
            <span className="text-[9px] font-mono text-cyan-400 tracking-wider truncate">
              DEEP-TECH DEFENCE
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Section */}
      <div className="p-3 space-y-1 overflow-y-auto flex-1">
        <div className="px-3 py-1.5 text-[10px] font-mono tracking-widest text-slate-500 uppercase">
          OPERATIONAL MODULES
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center justify-between px-3 py-2 rounded-xs text-xs font-mono tracking-wider transition-all duration-100 group relative',
                  isActive
                    ? 'bg-cyan-950/40 text-cyan-300 border-l-2 border-cyan-400 font-medium pl-[10px]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                )
              }
            >
              <div className="flex items-center gap-3">
                <span className="transition-colors group-hover:text-cyan-400">{item.icon}</span>
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer / System Security Assurance with NETRA Emblem */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/50 space-y-2">
        <div className="flex items-center gap-2 text-slate-400">
          <img
            src="/assets/netra-logo.png"
            alt="NETRA"
            className="w-7 h-7 rounded-xs border border-cyan-500/30 object-cover shrink-0"
          />
          <div className="flex flex-col min-w-0">
            <span className="text-[10px] font-mono font-bold tracking-wider text-slate-200 truncate">
              NETRA C2 SECURE
            </span>
            <span className="text-[8px] font-mono text-slate-500 truncate">
              BUILD 2026.09 // CLASSIFIED
            </span>
          </div>
        </div>
        <p className="text-[8px] font-mono text-slate-600 leading-tight">
          Next-Generation Evidence & Tactical Reasoning Assistant
        </p>
      </div>
    </aside>
  );
};
