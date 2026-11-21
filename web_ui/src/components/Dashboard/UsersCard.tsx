import React from 'react';
import { Users, User, Calendar, TrendingUp } from 'lucide-react';
import { DetailedStats } from '@/types';

interface UsersCardProps {
  stats?: DetailedStats | null;
}

export default function UsersCard({ stats }: UsersCardProps) {
  const totalUsers = stats?.total_users || 0;
  const activeUsers = stats?.active_users_7d || 0;

  const activePercentage = totalUsers > 0
    ? Math.round((activeUsers / totalUsers) * 100)
    : 0;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 transition-all hover:shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-900/20 text-cyan-400">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">User Statistics</h3>
            <p className="text-sm text-slate-400">Total registered users</p>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="text-3xl font-bold">
          {totalUsers.toLocaleString()}
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1 text-slate-400">
            <User className="h-4 w-4" />
            <span>Active (7d): {activeUsers}</span>
          </div>
          <div className="flex items-center gap-1 text-slate-400">
            <TrendingUp className="h-4 w-4" />
            <span>{activePercentage}% active</span>
          </div>
        </div>

        <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all"
            style={{ width: `${activePercentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}