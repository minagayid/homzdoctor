import { useEffect, useRef, useState } from 'react';
import type { ComponentType } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  ScanLine,
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

const PATIENT_MENU: NavItem[] = [
  { to: PATHS.dashboard, label: 'Dashboard', icon: LayoutDashboard },
  { to: PATHS.records, label: 'Records', icon: FileText },
  { to: PATHS.diagnosis, label: 'AI Diagnosis', icon: ScanLine },
  { to: PATHS.prescriptions, label: 'Prescriptions', icon: Pill },
  { to: PATHS.pharmacies, label: 'Pharmacies', icon: MapPin },
  { to: PATHS.appointments, label: 'Appointments', icon: CalendarDays },
  { to: PATHS.chat, label: 'Assistant', icon: Bot },
];

const DOCTOR_MENU: NavItem[] = [
  { to: PATHS.doctor, label: 'Console', icon: Stethoscope },
  { to: PATHS.prescriptions, label: 'Prescriptions', icon: Pill },
  { to: PATHS.appointments, label: 'Appointments', icon: CalendarDays },
  { to: PATHS.chat, label: 'Assistant', icon: Bot },
];

function Avatar({ initials, src }: { initials: string; src?: string }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-gradient text-sm font-semibold text-white shadow-soft">
      {src ? <img src={src} alt="Profile" className="h-full w-full object-cover" /> : initials}
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
          'group relative flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition',
          isActive
            ? 'bg-brand-50 text-brand-700 shadow-soft'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
        )
      }
    >
      {({ isActive }) => (
        <>
          <span
            className={cn(
              'absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand-gradient transition-opacity',
              isActive ? 'opacity-100' : 'opacity-0',
            )}
          />
          <Icon className={cn('h-4 w-4 transition', isActive ? 'text-brand-600' : 'text-slate-400 group-hover:text-slate-600')} />
          {label}
        </>
      )}
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
            <Avatar initials={initials} src={user?.avatarUrl} />
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-900">{displayName}</p>
              <p className="truncate text-xs text-slate-500">{email}</p>
            </div>
          </div>
          <div className="h-px bg-slate-100" />
          <div className="p-1">
            <button type="button" onClick={() => goTo(PATHS.profile)} className={menuItemClass}>
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
        <Avatar initials={initials} src={user?.avatarUrl} />
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
  const role = useAuthStore((s) => s.user?.role);
  const menu = role === 'doctor' || role === 'admin' ? DOCTOR_MENU : PATIENT_MENU;
  return (
    <aside className="hidden h-full w-64 shrink-0 flex-col overflow-hidden border-r border-slate-200 bg-white md:flex">
      {/* Brand header */}
      <div className="flex h-20 items-center border-b border-slate-200 px-4">
        <Link to={PATHS.landing} className="flex items-center gap-2.5">
          <div className="rounded-xl bg-brand-gradient p-2 shadow-glow">
            <Stethoscope className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">
            Homz<span className="text-gradient">Doctor</span>
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
