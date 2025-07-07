"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, TrendingUp, Brain, Clock } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface HistoricalMetric {
  timestamp: string;
  memory_count: number;
  api_response_time: number;
}

interface DatabaseMetrics {
  current_memory_count: number;
  api_response_time: number;
  api_status: string;
  growth_trend: 'up' | 'down' | 'stable';
  last_updated: string;
  historical_data: HistoricalMetric[];
}

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'up': return <TrendingUp className="h-4 w-4 text-green-400" />;
    case 'down': return <TrendingUp className="h-4 w-4 text-red-400 rotate-180" />;
    default: return <TrendingUp className="h-4 w-4 text-gray-400" />;
  }
};

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

const generateMockHistoricalData = (): HistoricalMetric[] => {
  const data: HistoricalMetric[] = [];
  const now = new Date();
  
  // Generate data for the last 12 hours
  for (let i = 20; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - (i * 30 * 60 * 1000)); // Every 30 minutes
    data.push({
      timestamp: timestamp.toISOString(),
      memory_count: Math.floor(Math.random() * 20) + 85, // 85-105 memories
      api_response_time: Math.floor(Math.random() * 40) + 20, // 20-60ms
    });
  }
  
  return data;
};

const generateMockMetrics = (): DatabaseMetrics => {
  const historicalData = generateMockHistoricalData();
  const current = historicalData[historicalData.length - 1];
  
  return {
    current_memory_count: 100,
    api_response_time: current.api_response_time,
    api_status: 'UP',
    growth_trend: 'up',
    last_updated: new Date().toISOString(),
    historical_data: historicalData,
  };
};

export const DatabaseMetricsCard: React.FC = () => {
  const [metrics, setMetrics] = useState<DatabaseMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Generate mock metrics
      const mockMetrics = generateMockMetrics();
      setMetrics(mockMetrics);
      setError(null);
    } catch (err) {
      setError('Failed to fetch database metrics');
      console.error('Database metrics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-green-400" />
            Database Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !metrics) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-red-400" />
            Database Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-400 text-center py-8">
            {error || 'No data available'}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-4">
        <CardTitle className="text-white flex items-center gap-2">
          <Database className="h-5 w-5 text-green-400" />
          Database Metrics
          <Badge 
            className={`ml-auto ${
              metrics.api_status === 'UP' ? 'bg-green-500' : 'bg-red-500'
            } text-white`}
          >
            {metrics.api_status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Memory Count */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-400" />
            <span className="text-zinc-300">Total Memories</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-white">
              {metrics.current_memory_count.toLocaleString()}
            </span>
            {getTrendIcon(metrics.growth_trend)}
          </div>
        </div>

        {/* API Response Time */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-yellow-400" />
            <span className="text-zinc-300">Response Time</span>
          </div>
          <span className="text-lg font-semibold text-white">
            {metrics.api_response_time}ms
          </span>
        </div>

        {/* Memory Growth Chart */}
        {metrics.historical_data.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-zinc-300">Memory Growth (12h)</h4>
            <div className="h-24">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics.historical_data}>
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={formatTime}
                    tick={{ fontSize: 10, fill: '#a1a1aa' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis 
                    tick={{ fontSize: 10, fill: '#a1a1aa' }}
                    axisLine={false}
                    tickLine={false}
                    width={30}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#18181b',
                      border: '1px solid #27272a',
                      borderRadius: '6px',
                      color: '#ffffff'
                    }}
                    labelFormatter={(value) => `Time: ${formatTime(value as string)}`}
                    formatter={(value: number) => [`${value} memories`, 'Count']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="memory_count" 
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 3, fill: '#22c55e' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Status Indicators */}
        <div className="pt-2 border-t border-zinc-800">
          <div className="flex justify-between items-center text-sm">
            <span className="text-zinc-400">Growth Trend</span>
            <div className="flex items-center gap-1 text-zinc-300">
              {getTrendIcon(metrics.growth_trend)}
              <span className="capitalize">{metrics.growth_trend}</span>
            </div>
          </div>
        </div>

        {/* Last Updated */}
        <div className="text-xs text-zinc-500 text-center pt-2">
          Last updated: {new Date(metrics.last_updated).toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
}; 