import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

type Tone = 'gray' | 'green' | 'red' | 'amber' | 'teal' | 'brand' | 'accent';

const tones: Record<Tone, string> = {
  gray: 'bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200',
  green: 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200',
  red: 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-200',
  amber: 'bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200',
  teal: 'bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200',
  brand: 'bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200',
  accent: 'bg-accent-50 text-accent-700 ring-1 ring-inset ring-accent-200',
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function Badge({ tone = 'gray', className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
