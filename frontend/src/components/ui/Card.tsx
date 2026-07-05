import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

type Variant = 'default' | 'elevated' | 'interactive' | 'glass' | 'flush';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: Variant;
}

const variants: Record<Variant, string> = {
  default: 'rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft',
  elevated: 'rounded-2xl border border-slate-200/60 bg-white p-6 shadow-card',
  interactive:
    'rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft card-hover cursor-pointer',
  glass: 'rounded-2xl glass p-6 shadow-card',
  flush: 'rounded-2xl border border-slate-200/80 bg-white shadow-soft overflow-hidden',
};

export function Card({ variant = 'default', className, ...props }: CardProps) {
  return <div className={cn(variants[variant], className)} {...props} />;
}
