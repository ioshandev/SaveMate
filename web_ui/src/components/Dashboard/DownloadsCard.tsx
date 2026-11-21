import React from 'react';
import { Download, FileDown, Clock, ExternalLink } from 'lucide-react';
import { DetailedStats } from '@/types';

interface DownloadsCardProps {
  stats?: DetailedStats | null;
}

export default function DownloadsCard({ stats }: DownloadsCardProps) {
  const totalProcessed = stats?.total_processed || 0;
  const totalHistory = stats?.total_history || 0;
  const totalFavorites = stats?.total_favorites || 0;
  const byPlatform = stats?.by_platform || {};

  const topPlatform = Object.entries(byPlatform)[0];
  const downloadRate = totalHistory > 0 && totalProcessed > 0
    ? Math.round((totalProcessed / totalHistory) * 100)
    : 0;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 transition-all hover:shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-900/20 text-blue-400">
            <Download className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Processing Stats</h3>
            <p className="text-sm text-slate-400">Media processing activity</p>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-cyan-400">
              {totalProcessed}
            </div>
            <div className="text-xs text-slate-400">Processed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">
              {totalHistory}
            </div>
            <div className="text-xs text-slate-400">History</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-400">
              {totalFavorites}
            </div>
            <div className="text-xs text-slate-400">Favorites</div>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">
            Processing rate: <span className="font-medium text-white">{downloadRate}%</span>
          </span>
          {topPlatform && (
            <div className="flex items-center gap-1 text-slate-400">
              <ExternalLink className="h-4 w-4" />
              <span>Top: {topPlatform[0]}</span>
            </div>
          )}
        </div>

        <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all"
            style={{ width: `${downloadRate}%` }}
          />
        </div>
      </div>
    </div>
  );
}