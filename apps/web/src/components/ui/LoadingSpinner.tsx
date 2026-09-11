import React from 'react';
import { clsx } from 'clsx';

interface LoadingSpinnerProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = 'ACQUIRING TELEMETRY...',
  size = 'md',
  className,
}) => {
  const sizeMap = {
    sm: 'h-4 w-4 border',
    md: 'h-7 w-7 border-2',
    lg: 'h-10 w-10 border-2',
  }[size];

  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3 p-6', className)}>
      <div className="relative flex items-center justify-center">
        {/* Outer rotating ring */}
        <div
          className={clsx(
            'rounded-full border-slate-700 border-t-cyan-400 animate-spin',
            sizeMap
          )}
        />
        {/* Inner center dot */}
        <div className="absolute h-1.5 w-1.5 rounded-full bg-cyan-400 animate-ping" />
      </div>
      {label && (
        <span className="font-mono text-xs text-slate-400 tracking-widest uppercase animate-pulse">
          {label}
        </span>
      )}
    </div>
  );
};
