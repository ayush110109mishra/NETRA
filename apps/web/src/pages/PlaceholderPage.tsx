import React from 'react';
import { Card } from '../components/ui/Card.js';
import { Badge } from '../components/ui/Badge.js';
import { EmptyState } from '../components/ui/EmptyState.js';

interface PlaceholderPageProps {
  title: string;
  moduleCode: string;
  description: string;
  icon: React.ReactNode;
  operationalScope: string;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  moduleCode,
  description,
  icon,
  operationalScope,
}) => {
  return (
    <div className="flex flex-col gap-5 max-w-6xl w-full mx-auto pb-6">
      {/* Module Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase flex items-center gap-2">
            <span>{title}</span>
            <span className="text-slate-600 font-normal">|</span>
            <span className="text-xs text-cyan-400 font-normal">{moduleCode}</span>
          </h1>
          <p className="text-xs font-mono text-slate-500">
            {description}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="cyan" size="sm">
            MODULE: {moduleCode}
          </Badge>
          <Badge variant="slate" size="sm">
            STATUS: STANDBY
          </Badge>
        </div>
      </div>

      {/* Main Tactical Card Container */}
      <Card
        title={`TACTICAL ${title.toUpperCase()} WORKSPACE`}
        subtitle="OPERATIONAL SHELL"
        badge={<Badge variant="slate">READY FOR PHASE 1</Badge>}
        className="min-h-[420px]"
        bodyClassName="flex items-center justify-center p-8"
      >
        <EmptyState
          title={`NO ACTIVE ${title.toUpperCase()} RECORDS`}
          description={operationalScope}
          code={`MODULE:${moduleCode}`}
          icon={icon}
        />
      </Card>
    </div>
  );
};
