"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Activity, Cpu, HardDrive, MemoryStick } from 'lucide-react';

interface SystemMetrics {
  timestamp: string;
  memory_count: number;
  api_response_time: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  api_status: string;
  docker_containers: number;
  docker_images: number;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'UP': return 'bg-green-500';
    case 'DOWN': return 'bg-red-500';
    default: return 'bg-yellow-500';
  }
};

const getUsageColor = (usage: number) => {
  if (usage < 60) return 'bg-green-500';
  if (usage < 80) return 'bg-yellow-500';
  return 'bg-red-500';
};

const generateMockMetrics = (): SystemMetrics => {
  return {
    timestamp: new Date().toISOString(),
    memory_count: 100,
    api_response_time: Math.floor(Math.random() * 50) + 15, // 15-65ms
    cpu_usage: Math.floor(Math.random() * 40) + 25, // 25-65%
    memory_usage: Math.floor(Math.random() * 30) + 45, // 45-75%
    disk_usage: Math.floor(Math.random() * 20) + 30, // 30-50%
    api_status: 'UP',
    docker_containers: 4,
    docker_images: 12,
  };
};

export const SystemHealthCard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Generate mock metrics
      const mockMetrics = generateMockMetrics();
      setMetrics(mockMetrics);
      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics');
      console.error('Metrics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-400" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
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
            <Activity className="h-5 w-5 text-red-400" />
            System Health
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
          <Activity className="h-5 w-5 text-blue-400" />
          System Health
          <Badge 
            className={`ml-auto ${getStatusColor(metrics.api_status)} text-white`}
          >
            {metrics.api_status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* CPU Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-blue-400" />
              <span className="text-zinc-300">CPU Usage</span>
            </div>
            <span className="text-white font-medium">{metrics.cpu_usage}%</span>
          </div>
          <Progress 
            value={metrics.cpu_usage} 
            className="h-2"
            style={{
              background: 'rgb(39, 39, 42)',
            }}
          />
        </div>

        {/* Memory Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <MemoryStick className="h-4 w-4 text-green-400" />
              <span className="text-zinc-300">Memory Usage</span>
            </div>
            <span className="text-white font-medium">{metrics.memory_usage}%</span>
          </div>
          <Progress 
            value={metrics.memory_usage} 
            className="h-2"
            style={{
              background: 'rgb(39, 39, 42)',
            }}
          />
        </div>

        {/* Disk Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-purple-400" />
              <span className="text-zinc-300">Disk Usage</span>
            </div>
            <span className="text-white font-medium">{metrics.disk_usage}%</span>
          </div>
          <Progress 
            value={metrics.disk_usage} 
            className="h-2"
            style={{
              background: 'rgb(39, 39, 42)',
            }}
          />
        </div>

        {/* API Response Time */}
        <div className="pt-2 border-t border-zinc-800">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-300">API Response</span>
            <span className="text-white font-medium">{metrics.api_response_time}ms</span>
          </div>
        </div>

        {/* Docker Info */}
        <div className="flex justify-between text-sm text-zinc-400">
          <span>Containers: {metrics.docker_containers}</span>
          <span>Images: {metrics.docker_images}</span>
        </div>

        {/* Last Updated */}
        <div className="text-xs text-zinc-500 text-center pt-2">
          Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
}; 