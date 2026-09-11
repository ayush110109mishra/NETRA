import React from 'react';
import { BrainCircuit, ShieldAlert, FileText, CheckCircle2, AlertOctagon } from 'lucide-react';
import { Card } from '../ui/Card.js';
import { Badge } from '../ui/Badge.js';
import { Button } from '../ui/Button.js';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { Assessment } from '@netra/shared';

interface AiAssessmentPanelProps {
  assessment?: Assessment;
  isLoading?: boolean;
  onViewEvidence?: () => void;
  onViewAnalysis?: () => void;
  className?: string;
}

export const AiAssessmentPanel: React.FC<AiAssessmentPanelProps> = ({
  assessment,
  isLoading,
  onViewEvidence,
  onViewAnalysis,
  className,
}) => {
  if (isLoading) {
    return (
      <Card title="NETRA AI ASSESSMENT" badge={<Badge variant="amber">SIMULATED</Badge>} className={className}>
        <LoadingSpinner label="SYNTHESIZING ADVISORY ASSESSMENT..." />
      </Card>
    );
  }

  const confidence = assessment?.confidence ?? 86;
  const evidenceCount = assessment?.evidence_count ?? 12;
  const sourcesCount = assessment?.sources_count ?? 8;
  const contradictionsCount = assessment?.contradictions_count ?? 2;

  return (
    <Card
      title="NETRA AI ASSESSMENT"
      subtitle="SITUATIONAL SYNTHESIS"
      badge={
        <div className="flex items-center gap-1.5">
          <Badge variant="amber" size="sm">
            SIMULATED
          </Badge>
          <Badge variant="cyan" size="sm">
            ADVISORY
          </Badge>
        </div>
      }
      headerAction={<BrainCircuit className="w-3.5 h-3.5 text-cyan-400 animate-pulse-subtle" />}
      className={`border-cyan-500/30 ${className}`}
      bodyClassName="p-4 flex flex-col justify-between gap-3 font-mono"
    >
      {/* Top Banner / Current Situation Title */}
      <div>
        <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1 tracking-wider uppercase">
          <span className="flex items-center gap-1 text-cyan-300">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            CURRENT SITUATION
          </span>
          <span className="text-amber-400">PRIORITY: {assessment?.priority ?? 'HIGH'}</span>
        </div>

        <p className="text-xs text-slate-200 leading-relaxed font-sans mt-1 bg-slate-900/50 p-2.5 border border-slate-800/80 rounded-xs">
          {assessment?.answer ||
            'Elevated activity detected in the selected sector. Cross-sensor correlation indicates non-standard radar emissions synchronized with an unidentified UAV flight vector.'}
        </p>
      </div>

      {/* Metrics Row: Confidence, Evidence, Sources, Contradictions */}
      <div className="grid grid-cols-4 gap-2 pt-1 border-t border-slate-800/80 text-center select-none">
        <div className="bg-slate-900/60 p-2 border border-slate-800 rounded-xs">
          <span className="block text-[9px] text-slate-400 uppercase tracking-widest">
            Confidence
          </span>
          <span className="text-sm font-bold text-emerald-400">{confidence}%</span>
        </div>

        <div className="bg-slate-900/60 p-2 border border-slate-800 rounded-xs">
          <span className="block text-[9px] text-slate-400 uppercase tracking-widest">
            Evidence
          </span>
          <span className="text-sm font-bold text-cyan-400">{String(evidenceCount).padStart(2, '0')}</span>
        </div>

        <div className="bg-slate-900/60 p-2 border border-slate-800 rounded-xs">
          <span className="block text-[9px] text-slate-400 uppercase tracking-widest">
            Sources
          </span>
          <span className="text-sm font-bold text-slate-200">{String(sourcesCount).padStart(2, '0')}</span>
        </div>

        <div className="bg-slate-900/60 p-2 border border-slate-800 rounded-xs">
          <span className="block text-[9px] text-slate-400 uppercase tracking-widest">
            Contradictions
          </span>
          <span className="text-sm font-bold text-amber-400">{String(contradictionsCount).padStart(2, '0')}</span>
        </div>
      </div>

      {/* Bottom Action Triggers */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div className="flex items-center gap-1.5 text-[9px] text-slate-500">
          <ShieldAlert className="w-3 h-3 text-cyan-500" />
          <span>Atul Python AI integration pending. Data is synthetic demo.</span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={<FileText className="w-3 h-3" />}
            onClick={onViewEvidence}
          >
            VIEW EVIDENCE ({evidenceCount})
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={<AlertOctagon className="w-3 h-3" />}
            onClick={onViewAnalysis}
          >
            VIEW ANALYSIS
          </Button>
        </div>
      </div>
    </Card>
  );
};
