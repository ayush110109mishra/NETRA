import React from 'react';
import { clsx } from 'clsx';
import { ShieldAlert } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  code?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  code = 'STATUS: STANDBY',
  icon = <ShieldAlert className="w-8 h-8 text-slate-500" />,
  action,
  className,
}) => {
  return (
    <div
      className={clsx(
        'relative border border-dashed border-slate-800 bg-slate-950/40 p-8 rounded-sm flex flex-col items-center justify-center text-center tactical-cross-bg',
        className
      )}
    >
      <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-sm mb-3">
        {icon}
      </div>
      <span className="font-mono text-[10px] tracking-widest text-cyan-400/70 uppercase mb-1">
        [{code}]
      </span>
      <h3 className="font-mono text-sm font-semibold tracking-wider text-slate-200 uppercase mb-1">
        {title}
      </h3>
      <p className="text-xs text-slate-400 max-w-sm mb-4 leading-relaxed">
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};
