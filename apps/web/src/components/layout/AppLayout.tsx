import React from 'react';
import { Outlet } from 'react-router-dom';
import { CommandHeader } from '../dashboard/CommandHeader.js';
import { Sidebar } from './Sidebar.js';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-tactical-bg text-slate-200">
      {/* Top Tactical Command Header */}
      <CommandHeader />

      {/* Main Workspace Layout (Sidebar + Content Outlet) */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Tactical Content Viewport */}
        <main className="flex-1 overflow-y-auto tactical-grid-bg p-4 flex flex-col min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
