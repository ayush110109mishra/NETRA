import React, { useState } from 'react';
import { Compass, Box, FileText, Radio } from 'lucide-react';
import { Card } from '../ui/Card.js';
import { Badge } from '../ui/Badge.js';
import { TimelinePanel } from './TimelinePanel.js';
import { EntityPanel } from './EntityPanel.js';
import { EvidencePanel } from './EvidencePanel.js';
import { IntelligenceFeed } from './IntelligenceFeed.js';
import { Event, Entity, Evidence, IntelligenceFeedItem, SystemStatus } from '@netra/shared';

export type WorkspaceTab = 'TIMELINE' | 'ENTITIES' | 'EVIDENCE' | 'FEED';

interface MultiTabWorkspaceProps {
  events?: Event[];
  entities?: Entity[];
  evidence?: Evidence[];
  feedItems?: IntelligenceFeedItem[];
  systemStatus?: SystemStatus;
  isLoadingEvents?: boolean;
  isLoadingEntities?: boolean;
  isLoadingEvidence?: boolean;
  isLoadingFeed?: boolean;
  selectedEntityId?: string | null;
  selectedEventId?: string | null;
  onSelectEntity?: (entityId: string) => void;
  onSelectEvent?: (eventId: string) => void;
  className?: string;
}

export const MultiTabWorkspace: React.FC<MultiTabWorkspaceProps> = ({
  events = [],
  entities = [],
  evidence = [],
  feedItems = [],
  isLoadingEvents,
  isLoadingEntities,
  isLoadingEvidence,
  isLoadingFeed,
  selectedEntityId,
  selectedEventId,
  onSelectEntity,
  onSelectEvent,
  className,
}) => {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('TIMELINE');

  const tabs: { id: WorkspaceTab; label: string; count?: number; icon: React.ReactNode }[] = [
    {
      id: 'TIMELINE',
      label: 'EVENT TIMELINE',
      count: events.length,
      icon: <Compass className="w-3.5 h-3.5" />,
    },
    {
      id: 'ENTITIES',
      label: 'ENTITIES',
      count: entities.length,
      icon: <Box className="w-3.5 h-3.5" />,
    },
    {
      id: 'EVIDENCE',
      label: 'EVIDENCE',
      count: evidence.length,
      icon: <FileText className="w-3.5 h-3.5" />,
    },
    {
      id: 'FEED',
      label: 'INTEL FEED',
      count: feedItems.length,
      icon: <Radio className="w-3.5 h-3.5" />,
    },
  ];

  return (
    <Card
      title={
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono tracking-wider uppercase border-b-2 transition-all select-none cursor-pointer ${
                  isActive
                    ? 'border-cyan-400 text-cyan-300 font-bold bg-slate-900/60'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span
                    className={`text-[10px] px-1 py-0.2 rounded-xs ${
                      isActive ? 'bg-cyan-950 text-cyan-300' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      }
      badge={<Badge variant="slate">WORKSPACE: 70%</Badge>}
      headerClassName="p-0 px-2 bg-slate-950/60 border-b border-slate-800"
      className={`min-h-[380px] ${className}`}
      bodyClassName="p-4 max-h-[440px] overflow-y-auto"
    >
      {activeTab === 'TIMELINE' && (
        <TimelinePanel
          events={events}
          isLoading={isLoadingEvents}
          selectedEventId={selectedEventId}
          onSelectEvent={onSelectEvent}
        />
      )}

      {activeTab === 'ENTITIES' && (
        <EntityPanel
          entities={entities}
          isLoading={isLoadingEntities}
          selectedEntityId={selectedEntityId}
          onSelectEntity={onSelectEntity}
        />
      )}

      {activeTab === 'EVIDENCE' && (
        <EvidencePanel evidence={evidence} isLoading={isLoadingEvidence} />
      )}

      {activeTab === 'FEED' && (
        <IntelligenceFeed items={feedItems} isLoading={isLoadingFeed} />
      )}
    </Card>
  );
};
