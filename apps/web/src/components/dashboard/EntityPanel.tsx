import React from 'react';
import { Box } from 'lucide-react';
import { Entity } from '@netra/shared';
import { Badge } from '../ui/Badge.js';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { EmptyState } from '../ui/EmptyState.js';

interface EntityPanelProps {
  entities?: Entity[];
  isLoading?: boolean;
  selectedEntityId?: string | null;
  onSelectEntity?: (entityId: string) => void;
}

export const EntityPanel: React.FC<EntityPanelProps> = ({
  entities = [],
  isLoading,
  selectedEntityId,
  onSelectEntity,
}) => {
  if (isLoading) {
    return <LoadingSpinner label="LOADING TRACKED ENTITY INTELLIGENCE..." />;
  }

  if (entities.length === 0) {
    return (
      <EmptyState
        title="NO TRACKED ENTITIES"
        description="Zero tactical entities currently registered in the surveillance sector."
        code="REGISTRY: STANDBY"
      />
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'HOSTILE':
        return <Badge variant="red">HOSTILE</Badge>;
      case 'SURVEILLANCE':
        return <Badge variant="amber">SURVEILLANCE</Badge>;
      case 'ACTIVE':
        return <Badge variant="green">ACTIVE</Badge>;
      case 'STANDBY':
        return <Badge variant="cyan">STANDBY</Badge>;
      default:
        return <Badge variant="slate">{status}</Badge>;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
      {entities.map((entity) => {
        const isSelected = selectedEntityId === entity.entity_id;
        return (
          <div
            key={entity.entity_id}
            onClick={() => onSelectEntity && onSelectEntity(entity.entity_id)}
            className={`p-3.5 bg-slate-900/70 border rounded-xs cursor-pointer transition-all flex flex-col justify-between ${
              isSelected
                ? 'border-cyan-400 bg-slate-900/95 shadow-tactical-glow'
                : 'border-slate-800/80 hover:border-slate-700'
            }`}
          >
            {/* Header: ID, Name, Status */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <Box className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="font-bold text-slate-100">{entity.entity_id}</span>
                </div>
                {getStatusBadge(entity.status)}
              </div>

              <div className="text-[11px] font-semibold text-cyan-300 uppercase tracking-wider mb-2">
                {entity.name}
              </div>

              <p className="text-[11px] text-slate-300 font-sans leading-relaxed mb-3 bg-slate-950/50 p-2 border border-slate-800/70 rounded-xs">
                {entity.assessment}
              </p>
            </div>

            {/* Metrics Matrix: Risk, Anomaly, Confidence, Observations */}
            <div>
              <div className="grid grid-cols-4 gap-1.5 p-2 bg-slate-950/70 border border-slate-800/60 rounded-xs text-center mb-2 select-none">
                <div>
                  <span className="block text-[8px] text-slate-500 uppercase">Risk</span>
                  <span
                    className={`text-xs font-bold ${
                      entity.risk_score > 75
                        ? 'text-rose-400'
                        : entity.risk_score > 50
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {entity.risk_score}%
                  </span>
                </div>

                <div>
                  <span className="block text-[8px] text-slate-500 uppercase">Anomaly</span>
                  <span className="text-xs font-bold text-amber-400">{entity.anomaly_score}%</span>
                </div>

                <div>
                  <span className="block text-[8px] text-slate-500 uppercase">Confidence</span>
                  <span className="text-xs font-bold text-emerald-400">{entity.confidence}%</span>
                </div>

                <div>
                  <span className="block text-[8px] text-slate-500 uppercase">Detects</span>
                  <span className="text-xs font-bold text-slate-200">{entity.observations}</span>
                </div>
              </div>

              {/* Related events & evidence count footer */}
              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                <span>
                  RELATED EVENTS:{' '}
                  <span className="text-slate-300">
                    {entity.related_events.length > 0 ? entity.related_events.join(', ') : 'NONE'}
                  </span>
                </span>
                <span className="text-cyan-400">
                  EVIDENCE: {entity.evidence_count} RECORDS
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
