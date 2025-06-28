"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AlertTriangle, AlertCircle, Info, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';

interface Alert {
  timestamp: string;
  level: 'CRITICAL' | 'WARNING' | 'INFO';
  component: string;
  message: string;
  resolved: boolean;
}

interface AlertsSummary {
  alerts: Alert[];
  total_count: number;
  critical_count: number;
  warning_count: number;
  unresolved_count: number;
}

const getAlertIcon = (level: string) => {
  switch (level) {
    case 'CRITICAL': return <AlertCircle className="h-4 w-4 text-red-400" />;
    case 'WARNING': return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
    case 'INFO': return <Info className="h-4 w-4 text-blue-400" />;
    default: return <Info className="h-4 w-4 text-gray-400" />;
  }
};

const getAlertColor = (level: string) => {
  switch (level) {
    case 'CRITICAL': return 'bg-red-500';
    case 'WARNING': return 'bg-yellow-500';
    case 'INFO': return 'bg-blue-500';
    default: return 'bg-gray-500';
  }
};

const formatRelativeTime = (timestamp: string) => {
  const now = new Date();
  const alertTime = new Date(timestamp);
  const diffMs = now.getTime() - alertTime.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

export const AlertsCard: React.FC = () => {
  const [alertsData, setAlertsData] = useState<AlertsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('http://localhost:8766/api/v1/monitoring/alerts?hours=24');
      const alerts = response.data.alerts || [];
      
      // Calculate summary stats
      const criticalCount = alerts.filter((a: Alert) => a.level === 'CRITICAL').length;
      const warningCount = alerts.filter((a: Alert) => a.level === 'WARNING').length;
      const unresolvedCount = alerts.filter((a: Alert) => !a.resolved).length;
      
      setAlertsData({
        alerts: alerts.slice(0, 10), // Show only recent 10 alerts
        total_count: alerts.length,
        critical_count: criticalCount,
        warning_count: warningCount,
        unresolved_count: unresolvedCount
      });
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch alerts');
      console.error('Alerts fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            System Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !alertsData) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-400" />
            System Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-400 text-center py-8">
            {error || 'No alerts data available'}
          </div>
        </CardContent>
      </Card>
    );
  }

  const hasUnresolvedAlerts = alertsData.unresolved_count > 0;

  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-4">
        <CardTitle className="text-white flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-400" />
          System Alerts
          <Badge 
            className={`ml-auto ${
              hasUnresolvedAlerts ? 'bg-red-500' : 'bg-green-500'
            } text-white`}
          >
            {alertsData.unresolved_count} Active
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Alert Summary */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="space-y-1">
            <div className="text-2xl font-bold text-red-400">
              {alertsData.critical_count}
            </div>
            <div className="text-xs text-zinc-400">Critical</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold text-yellow-400">
              {alertsData.warning_count}
            </div>
            <div className="text-xs text-zinc-400">Warning</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold text-white">
              {alertsData.total_count}
            </div>
            <div className="text-xs text-zinc-400">Total (24h)</div>
          </div>
        </div>

        {/* Recent Alerts List */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Recent Alerts
          </h4>
          
          {alertsData.alerts.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-zinc-400">
              <CheckCircle className="h-5 w-5 mr-2 text-green-400" />
              All clear - No recent alerts
            </div>
          ) : (
            <ScrollArea className="h-32">
              <div className="space-y-2">
                {alertsData.alerts.map((alert, index) => (
                  <div 
                    key={index}
                    className={`p-2 rounded-lg border ${
                      alert.resolved 
                        ? 'bg-zinc-800/50 border-zinc-700 opacity-60' 
                        : 'bg-zinc-800 border-zinc-700'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <div className="mt-0.5">
                        {getAlertIcon(alert.level)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge 
                            className={`${getAlertColor(alert.level)} text-white text-xs px-1.5 py-0.5`}
                          >
                            {alert.level}
                          </Badge>
                          <span className="text-xs text-zinc-400">
                            {alert.component}
                          </span>
                          <span className="text-xs text-zinc-500 ml-auto">
                            {formatRelativeTime(alert.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm text-zinc-200 truncate" title={alert.message}>
                          {alert.message}
                        </p>
                        {alert.resolved && (
                          <div className="flex items-center gap-1 mt-1">
                            <CheckCircle className="h-3 w-3 text-green-400" />
                            <span className="text-xs text-green-400">Resolved</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>

        {/* Status Footer */}
        <div className="pt-2 border-t border-zinc-800">
          <div className="flex justify-between items-center text-xs text-zinc-500">
            <span>
              {hasUnresolvedAlerts 
                ? `${alertsData.unresolved_count} alerts need attention`
                : 'All alerts resolved'
              }
            </span>
            <span>Last 24 hours</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 