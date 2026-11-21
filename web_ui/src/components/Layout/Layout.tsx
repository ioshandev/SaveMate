import React from 'react';
import { useLocation, Outlet, Link } from 'react-router-dom';
import { SystemStatus, DetailedStats } from '@/types';
import {
  BarChart3,
  Users,
  Clock,
  Activity,
  Settings,
  LogOut,
  Shield,
  Database,
  Zap,
} from 'lucide-react';

interface LayoutProps {
  status: SystemStatus | null;
  stats: DetailedStats | null;
  onLogout: () => void;
}

const navigation = [
  { name: 'Overview', href: '/', icon: BarChart3 },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Activity', href: '/activity', icon: Activity },
];

export default function Layout({ status, stats, onLogout }: LayoutProps) {
  const location = useLocation();

  const isActive = (href: string) => location.pathname === href || (href !== '/' && location.pathname.startsWith(href));

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="hidden w-16 flex-col items-center bg-slate-900/50 border-r border-slate-800 px-2 py-4 sm:flex sm:w-64 lg:w-72">
        <div className="mb-8 flex justify-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white">
            <Shield className="h-5 w-5" />
          </div>
        </div>

        <nav className="flex flex-col items-center gap-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex w-full items-center justify-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-slate-800 ${
                  active ? 'bg-slate-800 text-cyan-400' : 'text-slate-300'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="hidden sm:inline">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto w-full">
          <div className="border-t border-slate-800 p-2">
            <button
              onClick={onLogout}
              className="flex w-full items-center justify-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-400 hover:bg-slate-800 transition-colors"
            >
              <LogOut className="h-5 w-5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="flex-1 flex flex-col sm:hidden">
        <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/50 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white">
              <Shield className="h-4 w-4" />
            </div>
            <h1 className="text-lg font-semibold">SaveMate</h1>
          </div>
          <button
            onClick={onLogout}
            className="rounded-lg p-2 text-slate-300 hover:bg-slate-800"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <Outlet />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}