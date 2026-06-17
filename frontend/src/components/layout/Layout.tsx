import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

/** App shell: top navbar + left sidebar + routed page content. */
export function Layout() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50">
      <Navbar />
      <div className="flex min-h-0 flex-1">
        <Sidebar />
        {/* Only this area scrolls; the sidebar stays fixed in place. */}
        <main className="min-w-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
