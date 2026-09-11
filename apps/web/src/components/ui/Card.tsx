import React from 'react';
import { clsx } from 'clsx';

export interface CardProps {
  title?: React.ReactNode;
  subtitle?: string;
  badge?: React.ReactNode;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  bodyClassName?: string;
  headerClassName?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  badge,
  headerAction,
  children,
  className,
  bodyClassName,
  headerClassName,
}) => {
  return (
    <div
      className={clsx(
        'tactical-card bg-tactical-surface/90 border border-slate-800/80 rounded-sm flex flex-col',
        className
      )}
    >
      {(title || badge || headerAction) && (
        <div
          className={clsx(
            'flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-900/30',
            headerClassName
          )}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            {typeof title === 'string' ? (
              <h3 className="text-xs font-mono font-semibold tracking-wider text-slate-200 uppercase truncate">
                {title}
              </h3>
            ) : (
              title
            )}
            {subtitle && (
              <span className="text-[11px] font-mono text-slate-500 tracking-normal truncate">
                // {subtitle}
              </span>
            )}
            {badge}
          </div>
          {headerAction && <div className="shrink-0 ml-2">{headerAction}</div>}
        </div>
      )}
      <div className={clsx('p-4 flex-1', bodyClassName)}>{children}</div>
    </div>
  );
};
