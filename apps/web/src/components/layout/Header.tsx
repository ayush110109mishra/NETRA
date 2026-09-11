import React from 'react';
import { Radio, ShieldCheck, Wifi, WifiOff } from 'lucide-react';
import { useZuluClock } from '../../hooks/useZuluClock.js';
import { useHealth } from '../../hooks/useHealth.js';
import { StatusIndicator } from '../ui/StatusIndicator.js';

export const Header: React.FC = () => {
  const { zuluTime, zuluDate } = useZuluClock();
  const { data: health, isSuccess, isLoading } = useHealth(5000);

  return (
    <header className="h-14 border-b border-slate-800 bg-tactical-header px-4 flex items-center justify-between shrink-0 select-none">
      {/* Brand & Platform Identification */}
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-8 h-8 rounded border border-cyan-500/40 bg-cyan-950/30 text-cyan-400">
          <Radio className="w-4 h-4 animate-pulse-subtle" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold tracking-wider text-slate-100">
              NETRA
            </span>
            <span className="text-slate-600 font-mono text-xs">/</span>
            <span className="font-mono text-xs tracking-widest text-cyan-400 uppercase">
              ASTRAVEDA DEFENCE
            </span>
          </div>
          <p className="text-[10px] font-mono text-slate-500 tracking-wider">
            SEE. UNDERSTAND. RESPOND.
          </p>
        </div>
      </div>

      {/* Center Operational Status Badges */}
      <div className="hidden md:flex items-center gap-4">
        {/* Watch Posture */}
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-900/60 border border-slate-800 rounded-xs">
          <span className="text-[10px] font-mono text-slate-400 uppercase">POSTURE:</span>
          <span className="text-[11px] font-mono font-semibold text-emerald-400 uppercase">
            DEFCON 4 // ADVISORY
          </span>
        </div>

        {/* Tactical Sector */}
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-900/60 border border-slate-800 rounded-xs">
          <span className="text-[10px] font-mono text-slate-400 uppercase">SECTOR:</span>
          <span className="text-[11px] font-mono text-cyan-300">NORTH-SECTOR-01</span>
        </div>
      </div>

      {/* Right Telemetry: Zulu Clock & Core API Health Link */}
      <div className="flex items-center gap-4">
        {/* Backend API Live Status */}
        <div
          className="flex items-center gap-2 px-2.5 py-1 bg-slate-900/80 border border-slate-800 rounded-xs"
          title={isSuccess ? `Core API v${health.version} - ${health.environment}` : 'Connecting to Core API...'}
        >
          {isLoading ? (
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="font-mono text-[10px] text-cyan-400">CONNECTING...</span>
            </div>
          ) : isSuccess ? (
            <div className="flex items-center gap-1.5">
              <Wifi className="w-3 h-3 text-emerald-400" />
              <StatusIndicator status="nominal" pulse={true} />
              <span className="font-mono text-[10px] text-slate-300 tracking-wider">
                CORE: {health.status}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5">
              <WifiOff className="w-3 h-3 text-rose-400" />
              <StatusIndicator status="critical" pulse={false} />
              <span className="font-mono text-[10px] text-rose-400 tracking-wider">
                OFFLINE
              </span>
            </div>
          )}
        </div>

        {/* Zulu / UTC Clock */}
        <div className="flex flex-col text-right font-mono">
          <span className="text-xs font-semibold text-slate-100 tracking-wider">
            {zuluTime}
          </span>
          <span className="text-[9px] text-slate-500 tracking-widest uppercase">
            {zuluDate}
          </span>
        </div>

        {/* Human In The Loop Advisory Guardrail */}
        <div className="hidden lg:flex items-center gap-1.5 pl-2 border-l border-slate-800 text-slate-400" title="AI Decision Advisory: Human-in-the-loop Active">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-[9px] tracking-widest uppercase text-slate-400">
            ADVISORY MODE
          </span>
        </div>
      </div>
    </header>
  );
};
