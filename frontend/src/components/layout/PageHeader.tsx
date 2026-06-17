import type { ComponentType, ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  icon?: ComponentType<{ className?: string }>;
  /** Optional right-aligned actions (e.g. an "Add" button). */
  actions?: ReactNode;
}

/**
 * Sticky page header. Stays pinned to the top of the scrollable content area
 * while the page body scrolls beneath it.
 */
export function PageHeader({ title, subtitle, icon: Icon, actions }: PageHeaderProps) {
  return (
    <div className="sticky top-0 z-10 flex h-20 items-center border-b border-slate-200 bg-slate-50/90 px-6 backdrop-blur">
      <div className="flex w-full items-center justify-between gap-4">
        <div className="min-w-0">
          <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-800">
            {Icon && <Icon className="h-6 w-6 shrink-0 text-teal-600" />}
            {title}
          </h1>
          {subtitle && <p className="mt-1 text-slate-600">{subtitle}</p>}
        </div>
        {actions && <div className="shrink-0">{actions}</div>}
      </div>
    </div>
  );
}
