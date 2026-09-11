import React from 'react';
import { FileSearch } from 'lucide-react';
import { Evidence } from '@netra/shared';
import { Badge } from '../ui/Badge.js';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { EmptyState } from '../ui/EmptyState.js';

interface EvidencePanelProps {
  evidence?: Evidence[];
  isLoading?: boolean;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidence = [],
  isLoading,
}) => {
  if (isLoading) {
    return <LoadingSpinner label="RETRIEVING EVIDENCE STORE..." />;
  }

  if (evidence.length === 0) {
    return (
      <EmptyState
        title="NO EVIDENCE RECORDS CORRELATED"
        description="Zero sensor intercepts or telemetry recordings linked to current operational filter."
        code="EVIDENCE: 0"
      />
    );
  }

  const getReliabilityBadge = (rel: string) => {
    switch (rel) {
      case 'CONFIRMED':
        return <Badge variant="green">CONFIRMED</Badge>;
      case 'PROBABLE':
        return <Badge variant="cyan">PROBABLE</Badge>;
      case 'DOUBTFUL':
        return <Badge variant="amber">DOUBTFUL</Badge>;
      default:
        return <Badge variant="slate">{rel}</Badge>;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
      {evidence.map((item) => (
        <div
          key={item.evidence_id}
          className="p-3 bg-slate-900/70 border border-slate-800/80 rounded-xs flex flex-col justify-between hover:border-slate-700 transition-colors"
        >
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <FileSearch className="w-3.5 h-3.5 text-cyan-400" />
                <span className="font-bold text-slate-100">{item.evidence_id}</span>
                <span className="text-[10px] text-slate-500">[{item.type}]</span>
              </div>
              {getReliabilityBadge(item.reliability)}
            </div>

            <div className="text-[10px] text-cyan-400 font-semibold mb-1">
              SOURCE: {item.source}
            </div>

            <p className="text-[11px] text-slate-300 font-sans leading-relaxed mb-2 bg-slate-950/40 p-2 border border-slate-800/60 rounded-xs">
              {item.summary}
            </p>
          </div>

          <div className="pt-2 border-t border-slate-800/60 text-[10px] text-slate-500 space-y-1">
            <div className="flex justify-between">
              <span>RELATIONSHIP:</span>
              <span className="text-slate-300 truncate max-w-[240px]">{item.relationship}</span>
            </div>
            <div className="flex justify-between">
              <span>CONFIDENCE:</span>
              <span className="text-emerald-400 font-semibold">{item.confidence}%</span>
            </div>
            <div className="flex justify-between">
              <span>INTERCEPT TIME:</span>
              <span>{new Date(item.timestamp).toLocaleTimeString()} UTC</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
