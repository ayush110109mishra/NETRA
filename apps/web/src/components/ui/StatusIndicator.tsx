import React from 'react';
import { clsx } from 'clsx';

export type StatusVariant = 'nominal' | 'warning' | 'critical' | 'standby' | 'cyan';

interface StatusIndicatorProps {
  status: StatusVariant;
  label?: string;
  pulse?: boolean;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  pulse = true,
  className,
}) => {
  const colors = {
    nominal: {
      dot: 'bg-emerald-400',
      ping: 'bg-emerald-400',
      text: 'text-emerald-400',
    },
    warning: {
      dot: 'bg-amber-400',
      ping: 'bg-amber-400',
      text: 'text-amber-400',
    },
    critical: {
      dot: 'bg-rose-500',
      ping: 'bg-rose-500',
      text: 'text-rose-400',
    },
    standby: {
      dot: 'bg-slate-500',
      ping: 'bg-slate-500',
      text: 'text-slate-400',
    },
    cyan: {
      dot: 'bg-cyan-400',
      ping: 'bg-cyan-400',
      text: 'text-cyan-400',
    },
  }[status];

  return (
    <div className={clsx('inline-flex items-center gap-2', className)}>
      <span className="relative flex h-2 w-2">
        {pulse && (
          <span
            className={clsx(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              colors.ping
            )}
          />
        )}
        <span className={clsx('relative inline-flex rounded-full h-2 w-2', colors.dot)} />
      </span>
      {label && (
        <span className={clsx('text-xs font-mono tracking-wider uppercase', colors.text)}>
          {label}
        </span>
      )}
    </div>
  );
};
