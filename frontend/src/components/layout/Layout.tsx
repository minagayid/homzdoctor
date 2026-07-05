import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

/** App shell: fixed left sidebar + routed page content (with its own sticky header). */
export function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      {/* Only this area scrolls; the sidebar stays fixed in place. */}
      <main className="relative min-w-0 flex-1 overflow-y-auto bg-slate-50 bg-mesh">
        <Outlet />
      </main>
    </div>
  );
}
