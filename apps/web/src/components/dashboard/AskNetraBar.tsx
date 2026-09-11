import React, { useState } from 'react';
import {
  BrainCircuit,
  Send,
  Sparkles,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';
import { useAskNetra } from '../../hooks/useIntelligence.js';
import { AskNetraResponse } from '@netra/shared';
import { Badge } from '../ui/Badge.js';
import { Button } from '../ui/Button.js';

interface AskNetraBarProps {
  className?: string;
}

export const AskNetraBar: React.FC<AskNetraBarProps> = ({ className }) => {
  const [query, setQuery] = useState('');
  const [lastResponse, setLastResponse] = useState<AskNetraResponse | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const askMutation = useAskNetra();

  const handleQuerySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || askMutation.isPending) return;

    askMutation.mutate(
      { query: query.trim() },
      {
        onSuccess: (response) => {
          setLastResponse(response);
          setIsExpanded(true);
        },
      }
    );
  };

  const handleQuickPrompt = (promptText: string) => {
    setQuery(promptText);
    askMutation.mutate(
      { query: promptText },
      {
        onSuccess: (response) => {
          setLastResponse(response);
          setIsExpanded(true);
        },
      }
    );
  };

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-40 bg-tactical-panel/95 backdrop-blur-md border-t border-cyan-500/40 shadow-2xl transition-all ${className}`}
    >
      {/* Collapsible Response Drawer */}
      {isExpanded && lastResponse && (
        <div className="max-w-6xl mx-auto p-4 border-b border-slate-800 font-mono text-xs max-h-80 overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-bold text-slate-100 uppercase">
                NETRA ADVISORY ASSESSMENT [SIMULATED]
              </span>
              <Badge variant="green" size="sm">
                CONFIDENCE: {lastResponse.confidence}%
              </Badge>
              <Badge variant="amber" size="sm">
                HUMAN-IN-THE-LOOP REQUIRED
              </Badge>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-slate-400 hover:text-slate-200 transition-colors p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2.5">
            <div>
              <span className="text-[10px] text-slate-500 uppercase">OPERATOR QUERY:</span>
              <p className="text-slate-300 font-sans italic mt-0.5">"{lastResponse.query}"</p>
            </div>

            <div>
              <span className="text-[10px] text-cyan-400 uppercase">SYNTHESIZED ADVISORY ANALYSIS:</span>
              <p className="text-slate-100 font-sans leading-relaxed bg-slate-950/70 p-3 border border-slate-800 rounded-xs mt-1">
                {lastResponse.response}
              </p>
            </div>

            {lastResponse.recommended_actions.length > 0 && (
              <div>
                <span className="text-[10px] text-amber-400 uppercase">RECOMMENDED ADVISORY ACTIONS:</span>
                <ul className="mt-1 space-y-1 font-sans text-slate-300">
                  {lastResponse.recommended_actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-cyan-400 font-mono text-xs">[{i + 1}]</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500">
              <div className="flex items-center gap-1 text-cyan-500">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>{lastResponse.guardrail_note}</span>
              </div>
              <div>SOURCES: {lastResponse.sources_used.join(', ')}</div>
            </div>
          </div>
        </div>
      )}

      {/* Persistent Input Bar */}
      <div className="max-w-6xl mx-auto px-4 py-2.5 flex flex-col md:flex-row items-center gap-3">
        <form onSubmit={handleQuerySubmit} className="w-full flex items-center gap-2">
          <div className="relative flex-1 flex items-center">
            <BrainCircuit className="absolute left-3 w-4 h-4 text-cyan-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask NETRA about this situation, entities, or sector anomalies..."
              disabled={askMutation.isPending}
              className="w-full pl-9 pr-24 py-2 bg-slate-950/90 border border-slate-700 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 rounded-xs font-mono text-xs text-slate-100 placeholder-slate-500 transition-colors"
            />
            {lastResponse && (
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="absolute right-2 px-2 py-1 text-[10px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 border border-slate-700 bg-slate-900 rounded-xs"
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronUp className="w-3 h-3" />}
                {isExpanded ? 'COLLAPSE' : 'SHOW ANSWER'}
              </button>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={!query.trim() || askMutation.isPending}
            icon={
              askMutation.isPending ? (
                <span className="w-3.5 h-3.5 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
              ) : (
                <Send className="w-3.5 h-3.5" />
              )
            }
          >
            {askMutation.isPending ? 'EVALUATING...' : 'QUERY'}
          </Button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="hidden lg:flex items-center gap-1.5 shrink-0 select-none">
          <span className="font-mono text-[9px] text-slate-500 uppercase">QUICK:</span>
          <button
            onClick={() => handleQuickPrompt('Analyze UAV flight anomaly ENT-UAV-09')}
            className="text-[10px] font-mono text-slate-400 hover:text-cyan-300 bg-slate-900/80 px-2 py-1 border border-slate-800 rounded-xs transition-colors"
          >
            UAV TRACK
          </button>
          <button
            onClick={() => handleQuickPrompt('Report active threats in Sector Alpha')}
            className="text-[10px] font-mono text-slate-400 hover:text-cyan-300 bg-slate-900/80 px-2 py-1 border border-slate-800 rounded-xs transition-colors"
          >
            SECTOR THREATS
          </button>
          <button
            onClick={() => handleQuickPrompt('System readiness and AI core status')}
            className="text-[10px] font-mono text-slate-400 hover:text-cyan-300 bg-slate-900/80 px-2 py-1 border border-slate-800 rounded-xs transition-colors"
          >
            SYSTEM STATUS
          </button>
        </div>
      </div>
    </div>
  );
};
