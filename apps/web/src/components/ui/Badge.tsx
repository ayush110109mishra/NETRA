import React from 'react';
import { clsx } from 'clsx';

export type BadgeVariant = 'cyan' | 'green' | 'amber' | 'red' | 'slate';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'cyan',
  size = 'sm',
  className,
}) => {
  const variantStyles = {
    cyan: 'bg-cyan-950/40 text-cyan-300 border-cyan-800/60',
    green: 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60',
    amber: 'bg-amber-950/40 text-amber-300 border-amber-800/60',
    red: 'bg-rose-950/40 text-rose-300 border-rose-800/60',
    slate: 'bg-slate-900/60 text-slate-300 border-slate-700/60',
  }[variant];

  const sizeStyles = {
    sm: 'text-[10px] px-2 py-0.5 tracking-wider font-mono',
    md: 'text-xs px-2.5 py-1 tracking-wider font-mono',
  }[size];

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 uppercase font-medium border rounded-xs select-none',
        variantStyles,
        sizeStyles,
        className
      )}
    >
      {children}
    </span>
  );
};
