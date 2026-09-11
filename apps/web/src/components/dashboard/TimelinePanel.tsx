import React from 'react';
import { Clock, Crosshair } from 'lucide-react';
import { Event, SeverityLevel } from '@netra/shared';
import { Badge } from '../ui/Badge.js';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { EmptyState } from '../ui/EmptyState.js';

interface TimelinePanelProps {
  events?: Event[];
  isLoading?: boolean;
  selectedEventId?: string | null;
  onSelectEvent?: (eventId: string) => void;
}

export const TimelinePanel: React.FC<TimelinePanelProps> = ({
  events = [],
  isLoading,
  selectedEventId,
  onSelectEvent,
}) => {
  if (isLoading) {
    return <LoadingSpinner label="LOADING OPERATIONAL TIMELINE..." />;
  }

  if (events.length === 0) {
    return (
      <EmptyState
        title="NO RECENT EVENTS"
        description="Event stream is currently quiescent. No correlated sensor events recorded."
        code="TIMELINE: EMPTY"
      />
    );
  }

  const getSeverityBadge = (sev: SeverityLevel) => {
    switch (sev) {
      case 'CRITICAL':
        return <Badge variant="red">CRITICAL</Badge>;
      case 'HIGH':
        return <Badge variant="amber">HIGH</Badge>;
      case 'MEDIUM':
        return <Badge variant="cyan">MEDIUM</Badge>;
      default:
        return <Badge variant="slate">INFO</Badge>;
    }
  };

  return (
    <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800 font-mono text-xs">
      {events.map((event) => {
        const isSelected = selectedEventId === event.event_id;
        return (
          <div
            key={event.event_id}
            onClick={() => onSelectEvent && onSelectEvent(event.event_id)}
            className={`relative p-3 bg-slate-900/60 border rounded-xs cursor-pointer transition-all ${
              isSelected
                ? 'border-cyan-400 bg-slate-900/90 shadow-tactical-glow'
                : 'border-slate-800/80 hover:border-slate-700'
            }`}
          >
            {/* Timeline node dot */}
            <span
              className={`absolute -left-[23px] top-4 w-3 h-3 rounded-full border-2 ${
                event.severity === 'CRITICAL'
                  ? 'border-rose-500 bg-rose-950'
                  : event.severity === 'HIGH'
                  ? 'border-amber-400 bg-amber-950'
                  : 'border-cyan-400 bg-cyan-950'
              }`}
            />

            <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-2">
                {getSeverityBadge(event.severity)}
                <span className="font-bold text-slate-200">{event.event_id}</span>
                <span className="text-slate-500 text-[10px]">[{event.type}]</span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>{new Date(event.timestamp).toLocaleTimeString()} UTC</span>
              </div>
            </div>

            <p className="text-slate-300 text-[11px] font-sans leading-relaxed mb-2">
              {event.assessment}
            </p>

            <div className="flex flex-wrap items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
              <div className="flex items-center gap-2">
                <Crosshair className="w-3 h-3 text-cyan-400" />
                <span>
                  {event.location.sector} ({event.location.latitude.toFixed(3)}°N, {event.location.longitude.toFixed(3)}°E)
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span>CONF: {event.confidence}%</span>
                <span>RISK: {event.risk_score}%</span>
                {event.entities.length > 0 && (
                  <span className="text-cyan-400">ENTITIES: {event.entities.join(', ')}</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
