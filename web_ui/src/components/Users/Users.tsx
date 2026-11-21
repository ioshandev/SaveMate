import React, { useState, useEffect } from 'react';
import { Users as UsersIcon, User, Search, RefreshCw, ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import { apiService } from '@/services/api';
import { User as UserType, UserList } from '@/types';

export default function Users() {
  const [users, setUsers] = useState<UserType[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchUsers();
  }, [page]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await apiService.getUsers(page, limit);
      const filtered = search.trim()
        ? data.users.filter(u =>
          u.username?.toLowerCase().includes(search.toLowerCase()) ||
          u.first_name?.toLowerCase().includes(search.toLowerCase()) ||
          u.last_name?.toLowerCase().includes(search.toLowerCase())
        )
        : data.users;

      setUsers(filtered);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent<HTMLInputElement>) => {
    setSearch(e.currentTarget.value);
    setPage(0);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatNumber = (num: number) => {
    if (num === null || num === undefined) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Users</h1>
          <p className="text-slate-400">Loading users...</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-lg bg-slate-800" />
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 animate-pulse rounded-lg bg-slate-800" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-slate-400">
          {total} total users • Page {page + 1} of {totalPages}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search users..."
                value={search}
                onChange={handleSearch}
                className="rounded-lg border border-slate-700 bg-slate-800 py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-64"
              />
            </div>
          </div>

          <button
            onClick={() => {
              fetchUsers();
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
                <th className="px-4 py-3 text-left font-medium text-slate-400">ID</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">Language</th>
                <th className="px-4 py-3 text-right font-medium text-slate-400">Processed</th>
                <th className="px-4 py-3 text-right font-medium text-slate-400">History</th>
                <th className="px-4 py-3 text-right font-medium text-slate-400">Favorites</th>
                <th className="px-4 py-3 text-left font-medium text-slate-400">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                    {search ? 'No users found matching your search' : 'No users found'}
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-900/20 text-cyan-400">
                          <User className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="font-medium text-white">
                            {user.first_name || user.username || 'N/A'}
                            {user.last_name && ` ${user.last_name}`}
                          </div>
                          {user.username && (
                            <div className="text-xs text-slate-400">@{user.username}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <code className="rounded bg-slate-800 px-2 py-0.5 text-xs text-cyan-400">
                        {user.id}
                      </code>
                    </td>
                    <td className="px-4 py-3">
                      <span className="uppercase text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {user.language || 'en'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-cyan-400 font-medium">
                        {formatNumber(user.total_processed)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-slate-300">
                        {user.history_count || 0}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-purple-400 font-medium">
                        {user.favorites_count || 0}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-slate-400 text-sm">
                        {formatDate(user.registered_at)}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="flex items-center gap-1 rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
              Prev
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="flex items-center gap-1 rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}