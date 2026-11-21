import React, { useState, useEffect } from 'react';
import { DetailedStats, DailyStats, PlatformStats, SystemStatus } from '@/types';
import { apiService } from '@/services/api';
import StatsCard from './StatsCard';
import BotStatusCard from './BotStatusCard';
import UsersCard from './UsersCard';
import DownloadsCard from './DownloadsCard';
import {
  User,
  Activity,
  Database,
  Share2,
  Clock,
  CheckCircle,
  RefreshCw,
  BarChart3,
  Shield,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
  CartesianGrid,
} from 'recharts';

interface DashboardProps {
  stats?: DetailedStats | null;
}

export default function Dashboard({ stats: propsStats }: DashboardProps) {
  const [stats, setStats] = useState<DetailedStats | null>(propsStats || null);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    if (propsStats) {
      setStats(propsStats);
    }
    fetchData();
  }, [propsStats]);

  const fetchData = async () => {
    setLoading(!propsStats);
    try {
      const [statsData, dailyData, platformData] = await Promise.all([
        apiService.getStats(),
        apiService.getDailyStats(30),
        apiService.getPlatformStats(),
      ]);

      setStats(statsData);
      setDailyStats(dailyData);
      setPlatformStats(platformData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num === null || num === undefined) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const COLORS = ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

  // Convert by_platform dict to array for charts
  const platformChartData = React.useMemo(() => {
    if (!stats?.by_platform) return [];
    return Object.entries(stats.by_platform).map(([platform, count]) => ({
      platform,
      count,
    }));
  }, [stats?.by_platform]);

  // Show loading only when we don't have data yet
  const hasData = stats !== null && stats !== undefined;
  if (loading && !hasData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-slate-400">Loading...</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl bg-slate-800" />
          ))}
        </div>
      </div>
    );
  }

  const activeUsers = stats?.active_users_7d || 0;
  const totalUsers = stats?.total_users || 0;
  const totalProcessed = stats?.total_processed || 0;
  const totalHistory = stats?.total_history || 0;
  const totalFavorites = stats?.total_favorites || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-slate-400">
            Last updated: {lastUpdated?.toLocaleString() || 'Never'}
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium hover:bg-slate-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={formatNumber(totalUsers)}
          change={totalUsers > 0 ? `+${totalUsers} users` : 'No users'}
          icon={<User className="h-5 w-5" />}
          color="cyan"
        />
        <StatsCard
          title="Active Users (7d)"
          value={formatNumber(activeUsers)}
          change={`${activeUsers > 0 ? '↑' : '→'} Active`}
          icon={<Activity className="h-5 w-5" />}
          color="green"
        />
        <StatsCard
          title="Total Processed"
          value={formatNumber(totalProcessed)}
          change={`${formatNumber(totalProcessed)} actions`}
          icon={<Database className="h-5 w-5" />}
          color="blue"
        />
        <StatsCard
          title="History Entries"
          value={formatNumber(totalHistory)}
          change={`${formatNumber(totalHistory)} records`}
          icon={<Clock className="h-5 w-5" />}
          color="yellow"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Daily Activity Chart */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold">
            <BarChart3 className="h-5 w-5 text-cyan-400" />
            Daily Activity (Last 30 Days)
          </h2>
          {dailyStats.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8' }} />
                <YAxis tick={{ fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '0.5rem',
                  }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Line
                  type="monotone"
                  dataKey="processed_count"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="user_count"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-[200px] items-center justify-center">
              <p className="text-slate-500">No activity data available</p>
            </div>
          )}
        </div>

        {/* Platform Distribution */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold">
            <Share2 className="h-5 w-5 text-cyan-400" />
            Platform Distribution
          </h2>
          {platformChartData.length > 0 ? (
            <div className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={platformChartData}
                    dataKey="count"
                    nameKey="platform"
                    cx="50%"
                    cy="50%"
                    outerRadius={60}
                    innerRadius={30}
                    label={(entry) => entry.platform}
                  >
                    {platformChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend
                    verticalAlign="bottom"
                    horizontalAlign="center"
                    wrapperStyle={{ top: 20 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-[200px] items-center justify-center">
              <p className="text-slate-500">No platform data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Bot Status */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="mb-4 text-xl font-semibold">Bot Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Bot Status</span>
              </div>
              <span className="font-medium">Running</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-cyan-400" />
                <span>Database</span>
              </div>
              <span className="font-medium text-green-400">Connected</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-yellow-400" />
                <span>API Authentication</span>
              </div>
              <span className="font-medium">
                {stats ? 'Configured' : 'Not Configured'}
              </span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 lg:col-span-2">
          <h2 className="mb-4 text-xl font-semibold">Quick Actions</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <button className="rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 p-4 text-left transition hover:from-cyan-500 hover:to-blue-500">
              <div className="text-sm text-slate-300">View All Users</div>
              <div className="text-2xl font-bold text-white">{totalUsers}</div>
            </button>
            <button className="rounded-lg bg-gradient-to-r from-green-600 to-emerald-600 p-4 text-left transition hover:from-green-500 hover:to-emerald-500">
              <div className="text-sm text-slate-300">Total Processing</div>
              <div className="text-2xl font-bold text-white">{formatNumber(totalProcessed)}</div>
            </button>
            <button className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 p-4 text-left transition hover:from-purple-500 hover:to-pink-500">
              <div className="text-sm text-slate-300">Favorites</div>
              <div className="text-2xl font-bold text-white">{formatNumber(totalFavorites)}</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}