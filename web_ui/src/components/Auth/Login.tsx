import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiService } from '@/services/api';
import { SystemStatus, HealthResponse } from '@/types';
import { Shield, AlertCircle, Loader2, Key } from 'lucide-react';

interface LoginProps {
  onLogin: (apiKey: string) => void;
  status?: SystemStatus | null;
}

export default function Login({ onLogin, status }: LoginProps) {
  const [apiKey, setApikey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Get the from location if it exists
  const from = (location.state as any)?.from?.pathname || '/';

  // Check API health on mount
  React.useEffect(() => {
    apiService.healthCheck()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    setLoading(true);

    try {
      // Test the API key by making a request
      await apiService.getStats();
      onLogin(apiKey);
      navigate(from, { replace: true });
    } catch (err: any) {
      if (err.message?.includes('401') || err.message?.includes('Invalid API key')) {
        setError('Invalid API key. Please check and try again.');
      } else if (err.message?.includes('403')) {
        setError('Access denied. Contact the administrator.');
      } else {
        setError('Unable to connect to the API. Please check the connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-slate-900/50 p-8 border border-slate-800">
        <div className="text-center">
          <div className="mb-4 flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white">
              <Shield className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-2xl font-bold">SaveMate Dashboard</h1>
          <p className="mt-2 text-slate-400">Admin Panel Access</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-lg bg-red-900/20 p-3 text-sm text-red-400 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          <div>
            <label htmlFor="api-key" className="block text-sm font-medium text-slate-300 mb-2">
              API Key
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
              <input
                id="api-key"
                name="api-key"
                type="password"
                autoComplete="current-password"
                required
                value={apiKey}
                onChange={(e) => setApikey(e.target.value)}
                className="absolute inset-x-0 top-0 mx-auto w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-10 pr-4 text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="Enter your API key"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !health}
            className="relative w-full justify-center rounded-lg border border-transparent bg-gradient-to-r from-cyan-600 to-blue-600 px-4 py-3 text-sm font-medium text-white hover:from-cyan-500 hover:to-blue-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                Signing in...
              </>
            ) : (
              'Access Dashboard'
            )}
          </button>
        </form>

        {status && (
          <div className="mt-6 text-center text-sm text-slate-500">
            <p>API Status: {status.database}</p>
          </div>
        )}
      </div>
    </div>
  );
}