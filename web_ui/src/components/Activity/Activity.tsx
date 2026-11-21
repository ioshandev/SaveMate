import React, { useState, useEffect } from 'react';
import { History, MessageCircle, RefreshCw, ChevronLeft, ChevronRight, Search, FileDown, Heart } from 'lucide-react';
import { apiService } from '@/services/api';
import { HistoryEntry } from '@/types';

export default function Activity() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await apiService.getHistory();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateText = (text: string | undefined, max: number) => {
    if (!text) return 'N/A';
    if (text.length <= max) return text;
    return text.slice(0, max - 3) + '...';
  };

  const getStatusColor = (status: string) => {
    if (status === 'success') {
      return 'bg-green-900/20 text-green-400';
    } else if (status === 'error') {
      return 'bg-red-900/20 text-red-400';
    }
    return 'bg-yellow-900/20 text-yellow-400';
  };

  const getActionIcon = (actionType: string) => {
    const type = actionType.toLowerCase();
    if (type.includes('download') || type.includes('save')) return <FileDown className="h-4 w-4" />;
    if (type.includes('favorite') || type.includes('bookmark')) return <Heart className="h-4 w-4" />;
    return <MessageCircle className="h-4 w-4" />;
  };

  const filteredHistory = search.trim()
    ? history.filter(h =>
        h.user_id?.toString().includes(search) ||
        h.action_type?.toLowerCase().includes(search.toLowerCase()) ||
        h.file_name?.toLowerCase().includes(search.toLowerCase())
      )
    : history;

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Activity</h1>
          <p className="text-slate-400">Loading activity...</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="mb-4">
            <div className="h-10 animate-pulse rounded-lg bg-slate-800 mb-3" />
          </div>
          <div className="space-y-3">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-20 animate-pulse rounded-lg bg-slate-800" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const total = history.length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Activity</h1>
        <p className="text-slate-400">
          {total} total activities
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search by user ID, action, or file..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-80"
              />
            </div>
          </div>

          <button
            onClick={() => {
              fetchHistory();
            }}
            className="flex items-center gap-2 rounded-lg bg-slate-800 px-3 py-2 text-sm font-medium hover:bg-slate-700 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="px-4 py-3 text-left font-medium text-slate-400">User</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">Action</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">File</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">Status</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">Time</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                    {search ? 'No activities found matching your search' : 'No activities found'}
                  </td>
                </tr>
              ) : (
                filteredHistory.map((activity) => (
                  <tr key={activity.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-white">
                        User #{activity.user_id}
                      </div>
                      <div className="text-xs text-slate-400">
                        {activity.platform || 'N/A'}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {getActionIcon(activity.action_type)}
                        <code className="rounded bg-slate-800 px-2 py-0.5 text-xs text-cyan-400">
                          {activity.action_type}
                        </code>
                      </div>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate">
                      <span className="text-slate-300 text-sm">
                        {truncateText(activity.file_name || undefined, 40)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.result_status)}`}>
                        {activity.result_status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-slate-400 text-sm">
                        {formatDate(activity.created_at)}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}