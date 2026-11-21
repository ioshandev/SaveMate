import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import Login from './components/Auth/Login';
import Layout from './components/Layout/Layout';
import Users from './components/Users/Users';
import Activity from './components/Activity/Activity';
import { apiService } from '@/services/api';
import { SystemStatus, DetailedStats } from '@/types';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (apiKey: string) => void;
  logout: () => void;
}

export const AuthContext = React.createContext<AuthContextType>({
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
});

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = React.useContext(AuthContext);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [apiKey, setApikey] = useState<string | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [stats, setStats] = useState<DetailedStats | null>(null);

  useEffect(() => {
    // Check for stored API key
    const storedKey = localStorage.getItem('savemate_api_key');
    if (storedKey) {
      setApikey(storedKey);
      apiService.setApiKey(storedKey);
      setIsAuthenticated(true);

      // Fetch initial data
      apiService.getSystemStatus().then(setStatus).catch(() => setStatus(null));
      apiService.getStats().then(setStats).catch(() => setStats(null));
    }
  }, []);

  const login = (key: string) => {
    localStorage.setItem('savemate_api_key', key);
    setApikey(key);
    apiService.setApiKey(key);
    setIsAuthenticated(true);

    // Fetch initial data
    apiService.getSystemStatus().then(setStatus).catch(() => setStatus(null));
    apiService.getStats().then(setStats).catch(() => setStats(null));
  };

  const logout = () => {
    localStorage.removeItem('savemate_api_key');
    setApikey(null);
    setIsAuthenticated(false);
    setStatus(null);
    setStats(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      <div className="min-h-screen bg-slate-900 text-slate-100">
        <Routes>
          <Route path="/login" element={
            <Login
              onLogin={login}
              status={status}
            />
          } />
          <Route element={
            <PrivateRoute>
              <Layout status={status} stats={stats} onLogout={logout} />
            </PrivateRoute>
          }>
            <Route path="/" element={<Dashboard stats={stats} />} />
            <Route path="/dashboard" element={<Dashboard stats={stats} />} />
            <Route path="/users" element={<Users />} />
            <Route path="/activity" element={<Activity />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AuthContext.Provider>
  );
}

export default App;