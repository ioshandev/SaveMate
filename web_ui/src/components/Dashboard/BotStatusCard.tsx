import React from 'react';
import { CheckCircle, XCircle, Database, AlertCircle } from 'lucide-react';
import { SystemStatus } from '@/types';

interface BotStatusCardProps {
  status?: SystemStatus | null;
}

export default function BotStatusCard({ status }: BotStatusCardProps) {
  const getStatusIcon = () => {
    if (!status || status.database !== 'connected') {
      return <XCircle className="h-5 w-5 text-red-400" />;
    }
    return <CheckCircle className="h-5 w-5 text-green-400" />;
  };

  const getStatusColor = () => {
    if (!status || status.database !== 'connected') {
      return 'border-red-500/20';
    }
    return 'border-green-500/20';
  };

  return (
    <div className={`rounded-xl border p-6 transition-all hover:shadow-xl ${getStatusColor()}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <h3 className="text-lg font-semibold">System Status</h3>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
          <span className="text-slate-400">Database</span>
          <span className="font-medium">
            {status?.database === 'connected' ? (
              <><CheckCircle className="inline h-4 w-4 mr-1 text-green-400" /> Connected</>
            ) : (
              <><XCircle className="inline h-4 w-4 mr-1 text-red-400" /> Disconnected</>
            )}
          </span>
        </div>

        <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
          <span className="text-slate-400">Authentication</span>
          <span className="font-medium">
            {status?.api_key_configured ? (
              <><CheckCircle className="inline h-4 w-4 mr-1 text-green-400" /> Configured</>
            ) : (
              <><AlertCircle className="inline h-4 w-4 mr-1 text-yellow-400" /> Not Set</>
            )}
          </span>
        </div>

        <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
          <span className="text-slate-400">API Key</span>
          <span className="font-medium text-cyan-400">
            {status?.api_key_configured ? 'Secured' : 'Disabled'}
          </span>
        </div>
      </div>
    </div>
  );
}