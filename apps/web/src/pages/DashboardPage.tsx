import React, { useState } from 'react';
import {
  useAssessment,
  useEntities,
  useAlerts,
  useEvents,
  useEvidence,
  useFeed,
} from '../hooks/useIntelligence.js';
import { KpiLayer } from '../components/dashboard/KpiLayer.js';
import { MapContainer } from '../components/dashboard/MapContainer.js';
import { AiAssessmentPanel } from '../components/dashboard/AiAssessmentPanel.js';
import { AlertsPanel } from '../components/dashboard/AlertsPanel.js';
import { MultiTabWorkspace } from '../components/dashboard/MultiTabWorkspace.js';
import { AskNetraBar } from '../components/dashboard/AskNetraBar.js';
import { Alert } from '@netra/shared';

export const DashboardPage: React.FC = () => {
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>('ENT-UAV-09');
  const [selectedEventId, setSelectedEventId] = useState<string | null>('EVT-2026-0819');

  // Intelligence Data Queries
  const { data: assessment, isLoading: isLoadingAssessment } = useAssessment();
  const { data: entities, isLoading: isLoadingEntities } = useEntities();
  const { data: alerts, isLoading: isLoadingAlerts } = useAlerts();
  const { data: events, isLoading: isLoadingEvents } = useEvents();
  const { data: evidence, isLoading: isLoadingEvidence } = useEvidence();
  const { data: feedItems, isLoading: isLoadingFeed } = useFeed();

  const handleFocusAlert = (alert: Alert) => {
    if (alert.entity_id) setSelectedEntityId(alert.entity_id);
    if (alert.event_id) setSelectedEventId(alert.event_id);
  };

  return (
    <div className="flex flex-col gap-4 max-w-[1920px] w-full mx-auto pb-20">
      {/* 1. Command KPI Layer */}
      <KpiLayer />

      {/* 2. Primary 30% Map + 70% Intelligence Display */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Contextual Tactical Map Panel (~30% -> 4 cols out of 12) */}
        <div className="lg:col-span-4">
          <MapContainer
            entities={entities}
            events={events}
            selectedEntityId={selectedEntityId}
            onSelectEntity={(id) => setSelectedEntityId(id)}
            className="h-[440px]"
          />
        </div>

        {/* Intelligence Dominant Area (~70% -> 8 cols out of 12) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          {/* Top: AI Assessment Panel */}
          <AiAssessmentPanel
            assessment={assessment}
            isLoading={isLoadingAssessment}
            onViewEvidence={() => {
              // Can switch tab or scroll to evidence
              const el = document.getElementById('tactical-workspace');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            onViewAnalysis={() => {
              const el = document.getElementById('tactical-workspace');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
          />

          {/* Bottom of 70% area: Tactical Alerts Panel */}
          <div>
            <AlertsPanel
              alerts={alerts}
              isLoading={isLoadingAlerts}
              onFocusAlert={handleFocusAlert}
              onInvestigateAlert={handleFocusAlert}
              className="h-[240px]"
            />
          </div>
        </div>
      </div>

      {/* 3. Lower Multi-Tab Workspace (Timeline, Entities, Evidence, Feed) */}
      <div id="tactical-workspace">
        <MultiTabWorkspace
          events={events}
          entities={entities}
          evidence={evidence}
          feedItems={feedItems}
          isLoadingEvents={isLoadingEvents}
          isLoadingEntities={isLoadingEntities}
          isLoadingEvidence={isLoadingEvidence}
          isLoadingFeed={isLoadingFeed}
          selectedEntityId={selectedEntityId}
          selectedEventId={selectedEventId}
          onSelectEntity={(id) => setSelectedEntityId(id)}
          onSelectEvent={(id) => setSelectedEventId(id)}
        />
      </div>

      {/* 4. Persistent Ask NETRA Bar */}
      <AskNetraBar />
    </div>
  );
};
