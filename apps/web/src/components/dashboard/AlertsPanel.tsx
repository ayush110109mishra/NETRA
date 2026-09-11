import React from 'react';
import { BellRing, Eye, Crosshair, FileSearch } from 'lucide-react';
import { Card } from '../ui/Card.js';
import { Badge } from '../ui/Badge.js';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { EmptyState } from '../ui/EmptyState.js';
import { Alert, SeverityLevel } from '@netra/shared';

interface AlertsPanelProps {
  alerts?: Alert[];
  isLoading?: boolean;
  onFocusAlert?: (alert: Alert) => void;
  onInvestigateAlert?: (alert: Alert) => void;
  onViewEvidence?: (alert: Alert) => void;
  className?: string;
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({
  alerts = [],
  isLoading,
  onFocusAlert,
  onInvestigateAlert,
  onViewEvidence,
  className,
}) => {
  const getSeverityBadge = (sev: SeverityLevel) => {
    switch (sev) {
      case 'CRITICAL':
        return <Badge variant="red">CRITICAL</Badge>;
      case 'HIGH':
        return <Badge variant="amber">HIGH</Badge>;
      case 'MEDIUM':
        return <Badge variant="cyan">MEDIUM</Badge>;
      case 'LOW':
        return <Badge variant="green">LOW</Badge>;
      case 'INFO':
      default:
        return <Badge variant="slate">INFO</Badge>;
    }
  };

  return (
    <Card
      title="TACTICAL ALERTS"
      subtitle="REALTIME THREATS"
      badge={
        <span className="text-[10px] font-mono bg-rose-950/40 text-rose-300 px-1.5 py-0.5 border border-rose-800/60 rounded-xs">
          {alerts.length} ALERTS
        </span>
      }
      headerAction={<BellRing className="w-3.5 h-3.5 text-rose-400" />}
      className={`flex flex-col ${className || 'h-full'}`}
      bodyClassName="p-0 overflow-y-auto divide-y divide-slate-800/60"
    >
      {isLoading ? (
        <LoadingSpinner label="STREAMING ALERTS..." />
      ) : alerts.length === 0 ? (
        <div className="p-6">
          <EmptyState
            title="NO ACTIVE ALERTS"
            description="All monitored sectors report nominal status. Zero threshold excursions."
            code="ALERTS: NOMINAL"
          />
        </div>
      ) : (
        alerts.map((alert) => (
          <div
            key={alert.alert_id}
            className="p-3 hover:bg-slate-900/50 transition-colors font-mono group"
          >
            {/* Top row: Severity badge, Alert ID, Time */}
            <div className="flex items-center justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-2">
                {getSeverityBadge(alert.severity)}
                <span className="text-xs font-bold text-slate-200">{alert.alert_id}</span>
              </div>
              <span className="text-[10px] text-slate-500">
                {new Date(alert.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {/* Title & Description */}
            <h4 className="text-[11px] font-semibold text-slate-200 leading-tight mb-1">
              {alert.title}
            </h4>
            <p className="text-[10px] text-slate-400 font-sans leading-relaxed mb-2">
              {alert.description}
            </p>

            {/* Entity/Event Association & Confidence */}
            <div className="flex flex-wrap items-center justify-between text-[9px] text-slate-500 mb-2 gap-1.5">
              <div className="flex items-center gap-2">
                {alert.entity_id && (
                  <span className="text-cyan-400 bg-cyan-950/30 px-1 py-0.5 border border-cyan-800/40 rounded-xs">
                    {alert.entity_id}
                  </span>
                )}
                {alert.event_id && (
                  <span className="text-amber-400 bg-amber-950/30 px-1 py-0.5 border border-amber-800/40 rounded-xs">
                    {alert.event_id}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span>CONF: {alert.confidence}%</span>
                <span>RISK: {alert.risk_score}%</span>
              </div>
            </div>

            {/* Action buttons: Investigate, Focus, View Evidence */}
            <div className="flex items-center justify-end gap-1.5 pt-1 border-t border-slate-800/50">
              <button
                onClick={() => onFocusAlert && onFocusAlert(alert)}
                className="text-[9px] text-cyan-400 hover:text-cyan-300 bg-slate-900 hover:bg-slate-800 px-2 py-1 border border-slate-700 rounded-xs flex items-center gap-1 transition-colors"
                title="Focus on map and context"
              >
                <Crosshair className="w-2.5 h-2.5" />
                FOCUS
              </button>

              <button
                onClick={() => onViewEvidence && onViewEvidence(alert)}
                className="text-[9px] text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 px-2 py-1 border border-slate-700 rounded-xs flex items-center gap-1 transition-colors"
                title="View linked evidence"
              >
                <FileSearch className="w-2.5 h-2.5" />
                EVIDENCE
              </button>

              <button
                onClick={() => onInvestigateAlert && onInvestigateAlert(alert)}
                className="text-[9px] text-amber-400 hover:text-amber-300 bg-slate-900 hover:bg-slate-800 px-2 py-1 border border-slate-700 rounded-xs flex items-center gap-1 transition-colors"
                title="Initiate investigation"
              >
                <Eye className="w-2.5 h-2.5" />
                INVESTIGATE
              </button>
            </div>
          </div>
        ))
      )}
    </Card>
  );
};
