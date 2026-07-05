import type { InputHTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/utils';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  icon?: ReactNode;
  error?: string;
};

export function Input({ label, icon, error, className, id, ...props }: InputProps) {
  return (
    <label className="block" htmlFor={id}>
      {label && <span className="mb-1.5 block text-sm font-medium text-slate-700">{label}</span>}
      <div className="relative">
        {icon && (
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            {icon}
          </span>
        )}
        <input
          id={id}
          className={cn(
            'w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-soft outline-none transition',
            'placeholder:text-slate-400',
            'focus:border-brand-500 focus:ring-4 focus:ring-brand-500/12',
            icon ? 'pl-10' : undefined,
            error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/12' : 'border-slate-300',
            className,
          )}
          {...props}
        />
      </div>
      {error && <span className="mt-1 block text-xs font-medium text-red-600">{error}</span>}
    </label>
  );
}
