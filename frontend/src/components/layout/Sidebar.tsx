import { useEffect, useRef, useState } from 'react';
import type { ComponentType } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Pill,
  MapPin,
  CalendarDays,
  Bot,
  Settings,
  LogOut,
  User,
  ChevronsUpDown,
  Stethoscope,
} from 'lucide-react';
import { PATHS } from '../../routes/paths';
import { cn } from '../../lib/utils';
import { useAuthStore } from '../../store/authStore';

type NavItem = { to: string; label: string; icon: ComponentType<{ className?: string }> };

const menu: NavItem[] = [
  { to: PATHS.dashboard, label: 'Dashboard', icon: LayoutDashboard },
  { to: PATHS.records, label: 'Records', icon: FileText },
  { to: PATHS.prescriptions, label: 'Prescriptions', icon: Pill },
  { to: PATHS.pharmacies, label: 'Pharmacies', icon: MapPin },
  { to: PATHS.appointments, label: 'Appointments', icon: CalendarDays },
  { to: PATHS.chat, label: 'Assistant', icon: Bot },
];

function Avatar({ initials }: { initials: string }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-teal-600 text-sm font-semibold text-white">
      {initials}
    </div>
  );
}

function Item({ to, label, icon: Icon }: NavItem) {
  return (
    <NavLink
      to={to}
      end={to === PATHS.dashboard}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition',
          isActive ? 'bg-teal-50 text-teal-700' : 'text-slate-600 hover:bg-slate-100',
        )
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </NavLink>
  );
}

function UserMenu() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  // Close on outside click or Escape.
  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onPointerDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onPointerDown);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  const displayName = user?.fullName?.trim() || 'Guest User';
  const email = user?.email || 'guest@homzdoctor.app';
  const initials = displayName
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  const goTo = (path: string) => {
    setOpen(false);
    navigate(path);
  };

  const handleLogout = () => {
    setOpen(false);
    logout();
    navigate(PATHS.landing);
  };

  const menuItemClass =
    'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100';

  return (
    <div ref={containerRef} className="relative border-t border-slate-200 p-3">
      {open && (
        <div className="absolute bottom-full left-3 right-3 mb-2 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg">
          {/* Header */}
          <div className="flex items-center gap-3 px-3 py-3">
            <Avatar initials={initials} />
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-900">{displayName}</p>
              <p className="truncate text-xs text-slate-500">{email}</p>
            </div>
          </div>
          <div className="h-px bg-slate-100" />
          <div className="p-1">
            <button type="button" onClick={() => goTo(PATHS.settings)} className={menuItemClass}>
              <User className="h-4 w-4 text-slate-500" />
              View profile
            </button>
            <button type="button" onClick={() => goTo(PATHS.settings)} className={menuItemClass}>
              <Settings className="h-4 w-4 text-slate-500" />
              Settings
            </button>
          </div>
          <div className="h-px bg-slate-100" />
          <div className="p-1">
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              Log out
            </button>
          </div>
        </div>
      )}

      {/* Trigger */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        className={cn(
          'flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left transition hover:bg-slate-100',
          open && 'bg-slate-100',
        )}
      >
        <Avatar initials={initials} />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-900">{displayName}</p>
          <p className="truncate text-xs text-slate-500">{email}</p>
        </div>
        <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 text-slate-400" />
      </button>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden h-full w-64 shrink-0 flex-col overflow-hidden border-r border-slate-200 bg-white md:flex">
      {/* Brand header */}
      <div className="flex h-20 items-center border-b border-slate-200 px-4">
        <Link to={PATHS.landing} className="flex items-center gap-2">
          <div className="rounded-lg bg-teal-600 p-1.5">
            <Stethoscope className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold text-slate-900">
            Homz<span className="text-teal-600">Doctor</span>
          </span>
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto p-4">
        <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Menu
        </p>
        <div className="flex flex-col gap-1">
          {menu.map((item) => (
            <Item key={item.to} {...item} />
          ))}
        </div>
      </nav>

      <UserMenu />
    </aside>
  );
}
