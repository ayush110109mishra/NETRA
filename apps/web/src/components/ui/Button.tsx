import React from 'react';
import { clsx } from 'clsx';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', icon, children, disabled, ...props }, ref) => {
    const baseStyles =
      'relative inline-flex items-center justify-center font-mono font-medium tracking-wider uppercase transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer';

    const variants = {
      primary:
        'bg-cyan-600/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 hover:border-cyan-400 active:bg-cyan-500/40',
      secondary:
        'bg-slate-800/60 text-slate-200 border border-slate-700 hover:bg-slate-700/60 hover:border-slate-600',
      outline:
        'bg-transparent text-slate-300 border border-slate-700 hover:border-cyan-500/50 hover:text-cyan-300',
      danger:
        'bg-rose-950/40 text-rose-300 border border-rose-800/60 hover:bg-rose-900/50 hover:border-rose-600',
      ghost:
        'bg-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent',
    }[variant];

    const sizes = {
      sm: 'text-xs px-2.5 py-1.5 gap-1.5',
      md: 'text-xs px-3.5 py-2 gap-2',
      lg: 'text-sm px-4 py-2.5 gap-2.5',
    }[size];

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={clsx(baseStyles, variants, sizes, className)}
        {...props}
      >
        {icon && <span className="shrink-0">{icon}</span>}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
