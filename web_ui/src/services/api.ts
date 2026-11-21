/** API service for SaveMate Dashboard */
import type {
  HealthResponse,
  SystemStatus,
  DetailedStats,
  User,
  UserList,
  ActivityEntry,
  DailyStats,
  PlatformStats,
  HistoryEntry,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiService {
  private apiKey: string | null = null;

  setApiKey(key: string) {
    this.apiKey = key;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        ...this.getHeaders(),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json() as Promise<T>;
  }

  // Public endpoints (no auth)
  async healthCheck(): Promise<HealthResponse> {
    return this.request('/health');
  }

  async botStatus(): Promise<SystemStatus> {
    return this.request('/bot-status');
  }

  // Alias for botStatus (used in App.tsx)
  async getSystemStatus(): Promise<SystemStatus> {
    return this.botStatus();
  }

  // Protected endpoints (require API key)
  async getStats(): Promise<DetailedStats> {
    return this.request<DetailedStats>('/stats');
  }

  async getUsers(page: number = 0, limit: number = 50): Promise<UserList> {
    const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    return this.request(`/users?${params}`);
  }

  async getUser(userId: number): Promise<User> {
    return this.request<User>(`/users/${userId}`);
  }

  async getRecentActivity(limit: number = 100, hours: number = 24): Promise<ActivityEntry[]> {
    const params = new URLSearchParams({ limit: limit.toString(), hours: hours.toString() });
    return this.request<ActivityEntry[]>(`/activity?${params}`);
  }

  async getHistory(limit: number = 100, offset: number = 0): Promise<HistoryEntry[]> {
    const params = new URLSearchParams({ limit: limit.toString(), offset: offset.toString() });
    return this.request<HistoryEntry[]>(`/history?${params}`);
  }

  async getDailyStats(days: number = 30): Promise<DailyStats[]> {
    const params = new URLSearchParams({ days: days.toString() });
    return this.request<DailyStats[]>(`/daily-stats?${params}`);
  }

  async getPlatformStats(): Promise<PlatformStats[]> {
    return this.request<PlatformStats[]>('/platforms');
  }
}

export const apiService = new ApiService();
export default apiService;