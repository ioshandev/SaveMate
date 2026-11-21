/** TypeScript type definitions for SaveMate Dashboard */

// API Configuration
export interface ApiConfig {
  baseUrl: string;
  apiKey: string;
}

// Health
export interface HealthResponse {
  status: string;
  timestamp: string;
  database: string;
  version?: string;
}

export interface SystemStatus {
  status: string;
  database: string;
  api_key_configured: boolean;
  checked_at: string;
}

// Bot Status
export interface BotStatusResponse {
  status: string;
  ai_available: boolean;
  database_connected: boolean;
  last_updated: string;
}

// Statistics
export interface PlatformStat {
  platform: string;
  count: number;
}

export interface MediaStat {
  media_type: string;
  count: number;
}

export interface DailyStats {
  date: string;
  user_count: number;
  processed_count: number;
  history_count: number;
  favorites_count: number;
}

export interface PlatformStats {
  platform: string;
  count: number;
  change?: number;
}

export interface UserSummaryStats {
  total_users: number;
  new_users_today: number;
  active_users: number;
  average_processed_per_user: number;
}

export interface DownloadStats {
  total_downloads: number;
  downloads_today: number;
  downloads_by_status: Record<string, number>;
  downloads_by_platform: Record<string, number>;
}

// Activity/Entry types
export interface ActivityEntry {
  id: number;
  user_id: number;
  username?: string | null;
  action_type: string;
  platform?: string | null;
  file_name?: string | null;
  file_size?: number | null;
  result_status: string;
  error_message?: string | null;
  created_at: string;
  original_url?: string | null;
  media_type?: string | null;
  thumbnail_url?: string | null;
}

// History entry (alias for ActivityEntry with different fields)
export type HistoryEntry = ActivityEntry;

export interface PublicStatsResponse {
  total_users: number;
  active_users_24h: number;
  active_users_7d: number;
  total_processed: number;
  total_history: number;
  total_favorites: number;
  platform_stats: PlatformStat[];
  media_stats: MediaStat[];
  first_user_registered?: string | null;
}

export interface AdminStatsResponse {
  user_stats: UserSummaryStats;
  download_stats: DownloadStats;
  recent_activity: ActivityEntry[];
  daily_stats: DailyStats[];
  platform_breakdown: Record<string, number>;
  media_breakdown: Record<string, number>;
  generated_at: string;
}

// DetailedStats for Dashboard
export interface DetailedStats {
  total_users: number;
  total_processed: number;
  total_history: number;
  total_favorites: number;
  active_users_24h: number;
  active_users_7d: number;
  platform_stats: PlatformStat[];
  media_stats: MediaStat[];
  by_platform?: Record<string, number>;
  by_media?: Record<string, number>;
}

// Users (matches UserStats from web_api)
export interface User {
  id: number;
  username?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  language: string;
  registered_at: string;
  total_processed: number;
  notifications_enabled: boolean;
  last_activity?: string | null;
  history_count?: number;
  favorites_count?: number;
}

export interface UserList {
  users: User[];
  total: number;
  page: number;
  limit: number;
}

// UI Types
export interface DashboardStats {
  totalUsers: number;
  totalProcessed: number;
  activeUsers: number;
  downloadsToday: number;
  successRate: number;
}

export type TimeRange = '24h' | '7d' | '30d';

export interface ChartDataItem {
  name: string;
  value: number;
  color?: string;
}

export type ResponseStatus = 'success' | 'error' | 'warning' | 'info';

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}