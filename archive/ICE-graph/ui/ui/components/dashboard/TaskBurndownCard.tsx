"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  ChevronDown, 
  ChevronRight, 
  TrendingDown, 
  Target, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Calendar,
  BarChart3,
  ExternalLink,
  Zap,
  Activity
} from 'lucide-react';
import axios from 'axios';
import { TaskDetailModal } from './TaskDetailModal';

// Helper function to check if a date is today
const isToday = (date: Date): boolean => {
  const today = new Date();
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
};

interface TaskBurndownData {
  totalTasks: number;
  completedTasks: number;
  remainingTasks: number;
  tasksAddedToday: number;
  tasksCompletedToday: number;
  burndownRate: number;
  projectedCompletion: string;
  sprintStartDate: string;
  sprintEndDate: string;
  dailyBurndown: {
    date: string;
    planned: number;
    actual: number;
    remaining: number;
  }[];
  tasksByPriority: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  tasksByStatus: {
    pending: number;
    active: number;
    complete: number;
    blocked: number;
  };
  recentlyCompleted: {
    id: string;
    name: string;
    completedAt: string;
    agent: string;
    duration: number;
  }[];
  upcomingTasks: {
  id: string;
  name: string;
    priority: string;
    assignedTo: string;
    estimatedDuration: number;
    dependencies: string[];
  }[];
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'bg-red-500';
    case 'high': return 'bg-orange-500';
    case 'medium': return 'bg-yellow-500';
    case 'low': return 'bg-blue-500';
    default: return 'bg-gray-500';
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'complete': return 'bg-green-500';
    case 'active': return 'bg-blue-500';
    case 'blocked': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

export const TaskBurndownCard: React.FC = () => {
  const [burndownData, setBurndownData] = useState<TaskBurndownData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [selectedView, setSelectedView] = useState<'overview' | 'burndown' | 'details'>('overview');
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);

  const fetchBurndownData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/bmad/tasks/burndown', { timeout: 5000 });
      
      if (response.data) {
        setBurndownData(response.data);
        setError(null);
      } else {
        throw new Error('Invalid task data format');
      }
    } catch (err) {
      console.error('Burndown fetch error:', err);
      setError('Failed to fetch task data');
      setBurndownData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBurndownData();
    const interval = setInterval(fetchBurndownData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const handleTaskClick = (task: any) => {
    setSelectedTask({
      ...task,
      type: 'story',
      status: task.status || 'pending',
      description: `Task managed by ${task.agent || task.assignedTo}`,
      progress: 0
    });
    setIsTaskModalOpen(true);
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-orange-400" />
            Task Burndown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !burndownData) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-red-400" />
            Task Burndown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">
              {error || 'No burndown data available'}
            </div>
            <Button 
              onClick={fetchBurndownData}
              variant="outline"
              className="bg-zinc-800 border-zinc-700 text-white hover:bg-zinc-700"
            >
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const completionPercentage = burndownData.totalTasks > 0 ? (burndownData.completedTasks / burndownData.totalTasks) * 100 : 0;
  const remainingDays = burndownData.sprintEndDate ? Math.ceil((new Date(burndownData.sprintEndDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)) : 0;

  return (
    <>
    <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader 
          className="cursor-pointer hover:bg-zinc-800 transition-colors"
          onClick={() => setExpanded(!expanded)}
        >
        <CardTitle className="text-white flex items-center gap-2">
            {expanded ? <ChevronDown className="h-4 w-4 text-gray-400" /> : <ChevronRight className="h-4 w-4 text-gray-400" />}
            <TrendingDown className="h-5 w-5 text-orange-400" />
            Task Burndown
            <div className="ml-auto flex items-center gap-2">
              <Badge className="bg-orange-500 text-white">
                {burndownData.remainingTasks} Left
              </Badge>
              <Badge className="bg-green-500 text-white">
                {burndownData.tasksCompletedToday} Today
              </Badge>
            </div>
        </CardTitle>
      </CardHeader>
        <CardContent className="space-y-4">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Completion</span>
              <span className="text-white font-medium">{completionPercentage.toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Burndown Rate</span>
              <span className="text-white font-medium">{burndownData.burndownRate}/day</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Days Remaining</span>
              <span className="text-white font-medium">{remainingDays}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Active Tasks</span>
              <span className="text-white font-medium">{burndownData.tasksByStatus.active}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1">
            <Progress value={completionPercentage} className="h-2" />
            <div className="flex justify-between text-xs text-gray-400">
              <span>{burndownData.completedTasks} completed</span>
              <span>{burndownData.remainingTasks} remaining</span>
            </div>
          </div>

          {/* Expanded Details */}
          {expanded && (
            <div className="space-y-4 border-t border-zinc-700 pt-4">
              {/* View Controls */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">View:</span>
                {(['overview', 'burndown', 'details'] as const).map((view) => (
                  <Button
                    key={view}
                    size="sm"
                    variant={selectedView === view ? "default" : "outline"}
                    className={`text-xs ${
                      selectedView === view 
                        ? 'bg-orange-500 text-white' 
                        : 'bg-zinc-800 border-zinc-700 text-gray-300 hover:bg-zinc-700'
                    }`}
                    onClick={() => setSelectedView(view)}
                  >
                    {view.charAt(0).toUpperCase() + view.slice(1)}
                  </Button>
                ))}
              </div>

              {/* Overview */}
              {selectedView === 'overview' && (
                <div className="space-y-4">
                  {/* Task Distribution */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Task Distribution</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-2">
                        <div className="text-xs text-gray-400">By Priority:</div>
                        {Object.entries(burndownData.tasksByPriority).map(([priority, count]) => (
                          <div key={priority} className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${getPriorityColor(priority)}`}></div>
                              <span className="text-gray-300 capitalize">{priority}</span>
                            </div>
                            <span className="text-white">{count}</span>
                          </div>
                        ))}
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs text-gray-400">By Status:</div>
                        {Object.entries(burndownData.tasksByStatus).map(([status, count]) => (
                          <div key={status} className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`}></div>
                              <span className="text-gray-300 capitalize">{status}</span>
                            </div>
                            <span className="text-white">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Projection */}
                  <div className="bg-zinc-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4 text-green-400" />
                      <span className="text-sm font-medium text-white">Projection</span>
                    </div>
                    <div className="text-sm text-gray-300">
                      At current rate ({burndownData.burndownRate} tasks/day), projected completion: 
                      <span className="text-green-400 font-medium ml-2">
                        {new Date(burndownData.projectedCompletion).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Burndown Chart Data */}
              {selectedView === 'burndown' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Daily Burndown (Last 10 Days)
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {burndownData.dailyBurndown.map((day, index) => (
                      <div key={day.date} className="flex items-center justify-between p-2 bg-zinc-800 rounded text-xs">
                        <span className="text-gray-300">{new Date(day.date).toLocaleDateString()}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-blue-400">Planned: {day.planned}</span>
                          <span className="text-green-400">Actual: {day.actual}</span>
                          <span className="text-white font-medium">Remaining: {day.remaining}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Task Details */}
              {selectedView === 'details' && (
                <div className="space-y-4">
                  {/* Recently Completed */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Recently Completed ({burndownData.recentlyCompleted.length})
                    </h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {burndownData.recentlyCompleted.map((task) => (
                        <div 
                          key={task.id} 
                          className="flex items-center justify-between p-2 bg-zinc-800 rounded text-xs cursor-pointer hover:bg-zinc-700 transition-colors"
                          onClick={() => handleTaskClick(task)}
                        >
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-3 w-3 text-green-400" />
                            <span className="text-gray-300">{task.name}</span>
                            <ExternalLink className="h-3 w-3 text-gray-400" />
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-400">{task.agent}</span>
                            <span className="text-green-400">{task.duration}h</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Upcoming Tasks */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Upcoming Tasks ({burndownData.upcomingTasks.length})
                    </h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {burndownData.upcomingTasks.map((task) => (
                        <div 
                          key={task.id} 
                          className="flex items-center justify-between p-2 bg-zinc-800 rounded text-xs cursor-pointer hover:bg-zinc-700 transition-colors"
                          onClick={() => handleTaskClick(task)}
                        >
                          <div className="flex items-center gap-2">
                            <Clock className="h-3 w-3 text-gray-400" />
                            <span className="text-gray-300">{task.name}</span>
                            <Badge variant="outline" className={`text-xs ${getPriorityColor(task.priority).replace('bg-', 'text-').replace('500', '400')} border-none`}>
                              {task.priority}
                            </Badge>
                            <ExternalLink className="h-3 w-3 text-gray-400" />
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-400">{task.assignedTo}</span>
                            <span className="text-blue-400">{task.estimatedDuration}h</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Last Updated */}
              <div className="text-xs text-gray-500 text-center pt-2 border-t border-zinc-700">
                Last updated: {new Date().toLocaleTimeString()} • Auto-refresh every minute
        </div>
        </div>
          )}
      </CardContent>
    </Card>

      {/* Task Detail Modal */}
      <TaskDetailModal 
        task={selectedTask}
        isOpen={isTaskModalOpen}
        onClose={() => {
          setIsTaskModalOpen(false);
          setSelectedTask(null);
        }}
      />
    </>
  );
}; 