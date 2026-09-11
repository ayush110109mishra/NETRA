import React from 'react';
import { Activity, BellRing, Box, BrainCircuit } from 'lucide-react';
import { IntelligenceFeedItem } from '@netra/shared';
import { LoadingSpinner } from '../ui/LoadingSpinner.js';
import { EmptyState } from '../ui/EmptyState.js';

interface IntelligenceFeedProps {
  items?: IntelligenceFeedItem[];
  isLoading?: boolean;
}

export const IntelligenceFeed: React.FC<IntelligenceFeedProps> = ({
  items = [],
  isLoading,
}) => {
  if (isLoading) {
    return <LoadingSpinner label="ACQUIRING INTEL BROADCAST STREAM..." />;
  }

  if (items.length === 0) {
    return (
      <EmptyState
        title="FEED QUIESCENT"
        description="No real-time broadcast updates emitted on this channel."
        code="STREAM: IDLE"
      />
    );
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'ALERT':
        return <BellRing className="w-3.5 h-3.5 text-rose-400" />;
      case 'ENTITY':
        return <Box className="w-3.5 h-3.5 text-amber-400" />;
      case 'ASSESSMENT':
        return <BrainCircuit className="w-3.5 h-3.5 text-cyan-400" />;
      case 'SYSTEM':
      default:
        return <Activity className="w-3.5 h-3.5 text-emerald-400" />;
    }
  };

  return (
    <div className="divide-y divide-slate-800/60 font-mono text-xs">
      {items.map((item) => (
        <div
          key={item.id}
          className="p-3 hover:bg-slate-900/50 transition-colors flex items-start gap-3"
        >
          <div className="mt-0.5 p-1 bg-slate-950 border border-slate-800 rounded-xs">
            {getCategoryIcon(item.category)}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-0.5">
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] text-cyan-400 font-bold uppercase">
                  [{item.category}]
                </span>
                <span className="text-slate-200 font-semibold truncate">{item.title}</span>
              </div>
              <span className="text-[10px] text-slate-500 shrink-0">
                {new Date(item.timestamp).toLocaleTimeString()}
              </span>
            </div>

            <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
              {item.detail}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};
