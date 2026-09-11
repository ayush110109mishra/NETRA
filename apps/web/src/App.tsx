import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  Compass,
  Box,
  BrainCircuit,
  BellRing,
  Activity,
  FileText,
  LineChart,
  ShieldAlert,
  Settings,
} from 'lucide-react';
import { ROUTES } from '@netra/shared';
import { AppLayout } from './components/layout/AppLayout.js';
import { DashboardPage } from './pages/DashboardPage.js';
import { PlaceholderPage } from './pages/PlaceholderPage.js';
import { NotFoundPage } from './pages/NotFoundPage.js';

// Centralized TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            {/* Operational Dashboard */}
            <Route index element={<DashboardPage />} />

            {/* Foundation Navigation Shells */}
            <Route
              path={ROUTES.MISSIONS}
              element={
                <PlaceholderPage
                  title="Missions Management"
                  moduleCode="MSN-OPS"
                  description="Multi-domain mission planning, tasking, and status monitoring."
                  icon={<Compass className="w-8 h-8 text-cyan-400" />}
                  operationalScope="Mission creation, waypoint routing, and operational status will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.ASSETS}
              element={
                <PlaceholderPage
                  title="Asset Fleet Management"
                  moduleCode="AST-REG"
                  description="Defence asset tracking, readiness telemetry, and equipment allocations."
                  icon={<Box className="w-8 h-8 text-cyan-400" />}
                  operationalScope="Asset inventory, readiness state management, and geo-tracking will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.INTELLIGENCE}
              element={
                <PlaceholderPage
                  title="Intelligence & Recon"
                  moduleCode="INTEL-REC"
                  description="Multi-source intelligence correlation, threat synthesis, and advisory briefs."
                  icon={<BrainCircuit className="w-8 h-8 text-cyan-400" />}
                  operationalScope="Intelligence feed ingestion and advisory decision support will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.ALERTS}
              element={
                <PlaceholderPage
                  title="Tactical Alerts"
                  moduleCode="ALT-MON"
                  description="Realtime critical incident notifications, threshold triggers, and escalation pathways."
                  icon={<BellRing className="w-8 h-8 text-amber-400" />}
                  operationalScope="Live alert streaming, severity triage, and operator acknowledgment will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.TELEMETRY}
              element={
                <PlaceholderPage
                  title="Telemetry Gateway"
                  moduleCode="TLM-GTY"
                  description="High-frequency hardware telemetry streams, sensor feeds, and link health."
                  icon={<Activity className="w-8 h-8 text-emerald-400" />}
                  operationalScope="WebSocket telemetry pipelines and sensor data visualizations will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.DOCUMENTS}
              element={
                <PlaceholderPage
                  title="Tactical Documents"
                  moduleCode="DOC-SEC"
                  description="Classified operational orders, situational reports, and doctrine repositories."
                  icon={<FileText className="w-8 h-8 text-cyan-400" />}
                  operationalScope="Secure document indexing, retrieval, and vector storage will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.ANALYTICS}
              element={
                <PlaceholderPage
                  title="Operational Analytics"
                  moduleCode="ANL-REP"
                  description="Historical trend analysis, mission readiness metrics, and sensor performance data."
                  icon={<LineChart className="w-8 h-8 text-cyan-400" />}
                  operationalScope="Recharts operational trend reporting and sensor diagnostics will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.AUDIT_LOGS}
              element={
                <PlaceholderPage
                  title="Security & Audit Logs"
                  moduleCode="SEC-AUD"
                  description="Immutable operator audit trails, access verification, and security posture logs."
                  icon={<ShieldAlert className="w-8 h-8 text-rose-400" />}
                  operationalScope="Comprehensive tamper-evident event audit trails will be available in Phase 1."
                />
              }
            />

            <Route
              path={ROUTES.SETTINGS}
              element={
                <PlaceholderPage
                  title="System Settings"
                  moduleCode="SYS-CFG"
                  description="Platform configurations, API connectivity, and operator preferences."
                  icon={<Settings className="w-8 h-8 text-slate-400" />}
                  operationalScope="System environment variables, security keys, and display preferences will be available in Phase 1."
                />
              }
            />

            {/* 404 Fallback */}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};
export default App;
