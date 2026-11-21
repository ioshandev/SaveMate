import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down';
}

export default function StatsCard({ title, value, change, icon, color = 'cyan' }: StatsCardProps) {
  const colorMap = {
    cyan: 'text-cyan-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
    pink: 'text-pink-400',
  };

  const bgColorMap = {
    cyan: 'bg-cyan-900/20',
    green: 'bg-green-900/20',
    blue: 'bg-blue-900/20',
    yellow: 'bg-yellow-900/20',
    red: 'bg-red-900/20',
    purple: 'bg-purple-900/20',
    pink: 'bg-pink-900/20',
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 transition-all hover:shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${colorMap[color as keyof typeof colorMap]}`}>
            {icon}
          </div>
          <div>
            <p className="text-sm text-slate-400">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        </div>
      </div>
      {change && (
        <div className="mt-3 text-xs text-slate-400">{change}</div>
      )}
    </div>
  );
}