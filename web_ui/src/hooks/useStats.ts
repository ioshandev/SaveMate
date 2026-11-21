import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import {
  DetailedStats,
  DailyStats,
  PlatformStats,
  ActivityEntry,
} from '@/types';

interface UseStatsReturn {
  stats: DetailedStats | null;
  dailyStats: DailyStats[];
  platformStats: PlatformStats[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useStats(days: number = 30): UseStatsReturn {
  const [stats, setStats] = useState<DetailedStats | null>(null);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [statsData, dailyData, platformData] = await Promise.all([
        apiService.getStats(),
        apiService.getDailyStats(days),
        apiService.getPlatformStats(),
      ]);

      setStats(statsData);
      setDailyStats(dailyData);
      setPlatformStats(platformData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [days]);

  return {
    stats,
    dailyStats,
    platformStats,
    loading,
    error,
    refetch: fetchData,
  };
}

interface UseActivityReturn {
  activity: ActivityEntry[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useActivity(limit: number = 100, hours: number = 24): UseActivityReturn {
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiService.getRecentActivity(limit, hours);
      setActivity(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch activity');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [limit, hours]);

  return {
    activity,
    loading,
    error,
    refetch: fetchData,
  };
}