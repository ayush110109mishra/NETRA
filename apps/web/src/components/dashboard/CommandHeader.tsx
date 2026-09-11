import React, { useState } from 'react';
import {
  Shield,
  ShieldCheck,
  Wifi,
  WifiOff,
  Bell,
  Activity,
  ChevronDown,
  Info,
} from 'lucide-react';
import { useZuluClock } from '../../hooks/useZuluClock.js';
import { useSystemStatus } from '../../hooks/useIntelligence.js';
import { useWebSocket } from '../../hooks/useWebSocket.js';
import { Badge } from '../ui/Badge.js';
import { StatusIndicator } from '../ui/StatusIndicator.js';

export const CommandHeader: React.FC = () => {
  const { zuluTime, zuluDate } = useZuluClock();
  const { data: systemStatus, isLoading: isStatusLoading } = useSystemStatus();
  const { status: wsStatus } = useWebSocket();
  const [showStatusModal, setShowStatusModal] = useState(false);

  return (
    <header className="border-b border-slate-800 bg-tactical-header px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shrink-0 select-none">
      {/* Brand & Platform Identity */}
      <div className="flex items-center gap-3">
        {/* Official ASTRAVEDA Corporate Emblem */}
        <div className="relative flex items-center justify-center h-9 w-9 rounded-sm border border-cyan-500/30 bg-black/90 overflow-hidden shrink-0 shadow-sm">
          <img
            src="/assets/astraveda-logo.jpg"
            alt="ASTRAVEDA"
            className="w-full h-full object-cover"
          />
        </div>
        {/* Official NETRA Reticle Eye Emblem */}
        <div className="relative flex items-center justify-center h-9 w-9 rounded-sm border border-cyan-500/40 bg-black/90 overflow-hidden shadow-tactical-glow shrink-0">
          <img
            src="/assets/netra-logo.png"
            alt="NETRA Emblem"
            className="w-full h-full object-cover scale-110"
          />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold tracking-wider text-slate-100">
              ASTRAVEDA
            </span>
            <span className="text-slate-600 font-mono text-xs">|</span>
            <span className="font-mono text-xs tracking-widest text-cyan-400 font-bold uppercase">
              NETRA
            </span>
            <span className="text-[10px] font-mono text-slate-400 hidden sm:inline">
              // INTELLIGENCE CORE
            </span>
          </div>
          <p className="text-[9px] font-mono text-slate-400 tracking-wider">
            NEXT-GENERATION EVIDENCE & TACTICAL REASONING ASSISTANT
          </p>
        </div>
      </div>

      {/* Center Subsystem Status Badges */}
      <div className="hidden xl:flex items-center gap-2 font-mono text-[11px]">
        {/* System Overall */}
        <button
          onClick={() => setShowStatusModal(!showStatusModal)}
          className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-900/80 border border-slate-800 rounded-xs hover:border-slate-700 transition-colors"
        >
          <span className="text-slate-500 text-[10px]">SYSTEM:</span>
          <span className="text-emerald-400 font-medium">
            {systemStatus?.system || (isStatusLoading ? 'CHECKING...' : 'OPERATIONAL')}
          </span>
          <ChevronDown className="w-3 h-3 text-slate-500" />
        </button>

        {/* AI Core: SIMULATION (Explicitly marked) */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-950/20 border border-amber-800/40 rounded-xs">
          <span className="text-amber-500 text-[10px]">AI CORE:</span>
          <span className="text-amber-400 font-bold tracking-wider">SIMULATION</span>
        </div>

        {/* Simulation Environment Pill */}
        <Badge variant="amber" size="sm" className="font-bold">
          DEMO DATA
        </Badge>

        {/* Secure Status */}
        <div className="flex items-center gap-1 px-2 py-1 bg-slate-900/60 border border-slate-800 text-slate-300 rounded-xs">
          <Shield className="w-3 h-3 text-cyan-400" />
          <span className="text-[10px] text-slate-400">SECURE C2</span>
        </div>
      </div>

      {/* Right Controls: Telemetry, Clock, Notifications */}
      <div className="flex items-center gap-3.5">
        {/* WebSocket Pipeline Indicator */}
        <div
          className="flex items-center gap-1.5 px-2 py-1 bg-slate-900/80 border border-slate-800 rounded-xs"
          title={`WebSocket Pipeline: ${wsStatus}`}
        >
          {wsStatus === 'CONNECTED' ? (
            <>
              <Wifi className="w-3 h-3 text-emerald-400" />
              <StatusIndicator status="nominal" pulse={true} />
              <span className="font-mono text-[10px] text-slate-300">WS: READY</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3 h-3 text-amber-400" />
              <StatusIndicator status="warning" pulse={true} />
              <span className="font-mono text-[10px] text-amber-400">WS: SYNCING</span>
            </>
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

        {/* Notification Bell */}
        <button
          className="relative p-1.5 bg-slate-900/80 border border-slate-800 rounded-xs text-slate-400 hover:text-slate-200 transition-colors"
          title="7 Active Alerts"
        >
          <Bell className="w-3.5 h-3.5" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-rose-500 text-slate-100 text-[9px] font-mono font-bold rounded-full flex items-center justify-center">
            7
          </span>
        </button>

        {/* Operator Clearance */}
        <div className="hidden md:flex items-center gap-1.5 pl-2 border-l border-slate-800 text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <div className="flex flex-col text-left">
            <span className="font-mono text-[10px] text-slate-200 leading-none">VIPER-01</span>
            <span className="font-mono text-[8px] text-cyan-500 tracking-wider">SECRET // OP</span>
          </div>
        </div>
      </div>

      {/* Subsystem Health Modal Overlay */}
      {showStatusModal && (
        <div className="absolute top-14 left-4 z-50 w-80 p-3 bg-slate-950 border border-slate-700 shadow-tactical-card rounded-xs font-mono text-xs text-slate-300">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
            <span className="font-bold text-slate-100 uppercase flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              Subsystem Readiness
            </span>
            <button
              onClick={() => setShowStatusModal(false)}
              className="text-slate-500 hover:text-slate-300"
            >
              ✕
            </button>
          </div>
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-400">SYSTEM:</span>
              <span className="text-emerald-400 font-semibold">{systemStatus?.system || 'OPERATIONAL'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-400">BACKEND:</span>
              <span className="text-emerald-400 font-semibold">{systemStatus?.backend || 'ONLINE'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-400">DATABASE:</span>
              <span className="text-emerald-400 font-semibold">{systemStatus?.database || 'ONLINE'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-400">AI CORE (ATUL):</span>
              <span className="text-amber-400 font-bold">SIMULATION</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-400">DATA STREAM:</span>
              <span className="text-cyan-400 font-semibold">{systemStatus?.data_stream || 'CONNECTED'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">WEBSOCKET:</span>
              <span className="text-emerald-400 font-semibold">{wsStatus}</span>
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex items-center gap-1">
            <Info className="w-3 h-3 text-cyan-400" />
            <span>AI logic decoupled. Advisory simulation active.</span>
          </div>
        </div>
      )}
    </header>
  );
};
