import React from 'react';
import { BellRing, Compass, Box, AlertTriangle, ShieldAlert, Sparkles } from 'lucide-react';
import { useKpis } from '../../hooks/useIntelligence.js';

export const KpiLayer: React.FC = () => {
  const { data: kpis, isLoading, isError } = useKpis();

  // Fallbacks if loading or error
  const alertsVal = isLoading ? '--' : String(kpis?.alerts ?? 7).padStart(2, '0');
  const eventsVal = isLoading ? '---' : String(kpis?.events ?? 186);
  const entitiesVal = isLoading ? '--' : String(kpis?.entities ?? 73);
  const anomaliesVal = isLoading ? '--' : String(kpis?.anomalies ?? 8).padStart(2, '0');
  const riskVal = isLoading ? '--%' : `${kpis?.risk ?? 72}%`;
  const confVal = isLoading ? '--%' : `${kpis?.confidence ?? 86}%`;

  const kpiItems = [
    {
      label: 'ALERTS',
      value: alertsVal,
      icon: <BellRing className="w-3.5 h-3.5 text-rose-400" />,
      color: 'text-rose-400',
      borderAccent: 'border-l-rose-500',
      tag: 'ACTIVE',
    },
    {
      label: 'EVENTS',
      value: eventsVal,
      icon: <Compass className="w-3.5 h-3.5 text-cyan-400" />,
      color: 'text-slate-100',
      borderAccent: 'border-l-cyan-500',
      tag: 'LOGGED',
    },
    {
      label: 'ENTITIES',
      value: entitiesVal,
      icon: <Box className="w-3.5 h-3.5 text-cyan-400" />,
      color: 'text-slate-100',
      borderAccent: 'border-l-cyan-500',
      tag: 'TRACKED',
    },
    {
      label: 'ANOMALIES',
      value: anomaliesVal,
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
      color: 'text-amber-400',
      borderAccent: 'border-l-amber-500',
      tag: 'DETECTED',
    },
    {
      label: 'RISK',
      value: riskVal,
      icon: <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />,
      color: 'text-amber-400',
      borderAccent: 'border-l-amber-500',
      tag: 'ELEVATED',
    },
    {
      label: 'CONFIDENCE',
      value: confVal,
      icon: <Sparkles className="w-3.5 h-3.5 text-emerald-400" />,
      color: 'text-emerald-400',
      borderAccent: 'border-l-emerald-500',
      tag: 'SYNTHETIC',
    },
  ];

  if (isError) {
    return (
      <div className="p-2 bg-rose-950/30 border border-rose-800 text-rose-400 font-mono text-xs flex items-center justify-between">
        <span>FAILED TO LOAD SYNTHETIC COMMAND KPIS</span>
        <span className="text-[10px] text-slate-400">CHECKING CORE API CONNECTION...</span>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 select-none">
      {kpiItems.map((item) => (
        <div
          key={item.label}
          className={`tactical-card bg-tactical-surface/95 border border-slate-800 p-2.5 flex flex-col justify-between border-l-2 ${item.borderAccent} hover:border-slate-700 transition-colors`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase">
              {item.label}
            </span>
            {item.icon}
          </div>
          <div className="flex items-baseline justify-between mt-1.5">
            <span className={`text-xl font-mono font-bold tracking-tight ${item.color}`}>
              {item.value}
            </span>
            <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider">
              {item.tag}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
