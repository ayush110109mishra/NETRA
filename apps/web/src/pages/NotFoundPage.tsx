import React from 'react';
import { Link } from 'react-router-dom';
import { AlertOctagon, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/Button.js';
import { ROUTES } from '@netra/shared';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center p-6 tactical-grid-bg">
      <div className="p-4 bg-rose-950/30 border border-rose-800/60 rounded-xs mb-4">
        <AlertOctagon className="w-10 h-10 text-rose-400" />
      </div>
      <span className="font-mono text-xs text-rose-400 tracking-widest uppercase mb-1">
        [ERROR 404: SECTOR COORDINATES NOT FOUND]
      </span>
      <h1 className="font-mono text-xl font-bold text-slate-100 uppercase tracking-wider mb-2">
        RESTRICTED / UNDEFINED VECTOR
      </h1>
      <p className="text-xs text-slate-400 max-w-md mb-6 leading-relaxed">
        The requested operational module or coordinate route does not exist within the NETRA tactical registry.
      </p>
      <Link to={ROUTES.DASHBOARD}>
        <Button variant="primary" icon={<ArrowLeft className="w-3.5 h-3.5" />}>
          RETURN TO SITUATIONAL DASHBOARD
        </Button>
      </Link>
    </div>
  );
};
