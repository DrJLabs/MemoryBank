"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  ChevronDown, 
  ChevronRight, 
  Users, 
  User, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Settings,
  Brain,
  Target,
  TrendingUp,
  Activity,
  Zap,
  Star,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';
import { TaskDetailModal } from './TaskDetailModal';
import { WorkflowDetailModal } from './WorkflowDetailModal';

interface AgentTask {
  id: string;
  name: string;
  type: 'story' | 'epic' | 'workflow' | 'checklist' | 'custom';
  status: 'pending' | 'active' | 'complete' | 'error';
  priority: 'low' | 'medium' | 'high' | 'critical';
  startTime?: string;
  estimatedDuration?: number;
  actualDuration?: number;
  storyId?: string;
  epicId?: string;
  workflowId?: string;
}

interface AgentMetrics {
  tasksCompleted: number;
  tasksActive: number;
  averageCompletionTime: number;
  successRate: number;
  workloadScore: number;
  efficiencyRating: number;
  collaborationScore: number;
}

interface Agent {
  id: string;
  name: string;
  type: 'pm' | 'po' | 'dev' | 'qa' | 'sm' | 'analyst' | 'game-sm' | 'custom';
  status: 'active' | 'idle' | 'busy' | 'offline';
  currentTasks: AgentTask[];
  completedTasksToday: number;
  metrics: AgentMetrics;
  specializations: string[];
  lastActivity: string;
  availability: number; // 0-100%
  currentWorkflow?: string;
  collaboratingWith?: string[];
}

const getAgentTypeIcon = (type: string) => {
  switch (type) {
    case 'pm': return <Settings className="h-4 w-4 text-blue-400" />;
    case 'po': return <Target className="h-4 w-4 text-purple-400" />;
    case 'dev': return <Brain className="h-4 w-4 text-green-400" />;
    case 'qa': return <CheckCircle className="h-4 w-4 text-yellow-400" />;
    case 'sm': return <Users className="h-4 w-4 text-orange-400" />;
    case 'analyst': return <TrendingUp className="h-4 w-4 text-cyan-400" />;
    case 'game-sm': return <Zap className="h-4 w-4 text-pink-400" />;
    default: return <User className="h-4 w-4 text-gray-400" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'bg-green-500';
    case 'busy': return 'bg-yellow-500';
    case 'idle': return 'bg-blue-500';
    case 'offline': return 'bg-gray-500';
    default: return 'bg-gray-500';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'complete': return <CheckCircle className="h-4 w-4 text-green-400" />;
    case 'active': return <Clock className="h-4 w-4 text-blue-400" />;
    case 'error': return <AlertCircle className="h-4 w-4 text-red-400" />;
    default: return <Clock className="h-4 w-4 text-gray-400" />;
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'text-red-400 border-red-500/30';
    case 'high': return 'text-orange-400 border-orange-500/30';
    case 'medium': return 'text-yellow-400 border-yellow-500/30';
    default: return 'text-gray-400 border-gray-500/30';
  }
};

const getEfficiencyColor = (rating: number) => {
  if (rating >= 90) return 'text-green-400';
  if (rating >= 75) return 'text-yellow-400';
  if (rating >= 60) return 'text-orange-400';
  return 'text-red-400';
};

export const AgentActivityTracker: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'name' | 'activity' | 'efficiency' | 'workload'>('activity');
  const [selectedTask, setSelectedTask] = useState<AgentTask | null>(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/bmad/agents/activity', { timeout: 5000 });
      
      if (response.data && Array.isArray(response.data)) {
        setAgents(response.data);
        setError(null);
      } else {
        setAgents([]);
        setError('No agent data available');
      }
    } catch (err) {
      console.error('Agent activity fetch error:', err);
      setError('Failed to fetch agent activity data');
      // Set empty array to prevent perpetual loading
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const toggleAgentExpansion = (agentId: string) => {
    const newExpanded = new Set(expandedAgents);
    if (newExpanded.has(agentId)) {
      newExpanded.delete(agentId);
    } else {
      newExpanded.add(agentId);
    }
    setExpandedAgents(newExpanded);
  };

  const getSortedAgents = () => {
    return [...agents].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'activity':
          return b.currentTasks.length - a.currentTasks.length;
        case 'efficiency':
          return b.metrics.efficiencyRating - a.metrics.efficiencyRating;
        case 'workload':
          return b.metrics.workloadScore - a.metrics.workloadScore;
        default:
          return 0;
      }
    });
  };

  const getActiveAgentsCount = () => {
    return agents.filter(agent => agent.status === 'active' || agent.status === 'busy').length;
  };

  const getTotalActiveTasks = () => {
    return agents.reduce((total, agent) => total + agent.currentTasks.length, 0);
  };

  const handleTaskClick = (task: AgentTask, agent: Agent) => {
    // Enrich task with agent information
    const enrichedTask = {
      ...task,
      agent: agent.id,
      description: `Task assigned to ${agent.name} (${agent.type.toUpperCase()})`,
      progress: task.actualDuration && task.estimatedDuration 
        ? (task.actualDuration / task.estimatedDuration) * 100 
        : 0
    };
    setSelectedTask(enrichedTask);
    setIsTaskModalOpen(true);
  };

  const handleWorkflowClick = (workflowId: string) => {
    setSelectedWorkflowId(workflowId);
    setIsWorkflowModalOpen(true);
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-green-400" />
            Agent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || agents.length === 0) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-red-400" />
            Agent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">
              {error || 'No agent activity data available'}
            </div>
            <Button 
              onClick={fetchAgents}
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

  return (
    <>
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-green-400" />
            Agent Activity
            <div className="ml-auto flex items-center gap-2">
              <Badge className="bg-green-500 text-white">
                {getActiveAgentsCount()} Active
              </Badge>
              <Badge className="bg-blue-500 text-white">
                {getTotalActiveTasks()} Tasks
              </Badge>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Sort Controls */}
          <div className="flex items-center gap-2 pb-2 border-b border-zinc-700">
            <span className="text-sm text-gray-400">Sort by:</span>
            {(['name', 'activity', 'efficiency', 'workload'] as const).map((option) => (
              <Button
                key={option}
                size="sm"
                variant={sortBy === option ? "default" : "outline"}
                className={`text-xs ${
                  sortBy === option 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-zinc-800 border-zinc-700 text-gray-300 hover:bg-zinc-700'
                }`}
                onClick={() => setSortBy(option)}
              >
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </Button>
            ))}
          </div>

          {/* Agent List */}
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {getSortedAgents().map((agent) => (
              <div key={agent.id} className="space-y-2">
                {/* Agent Header */}
                <div 
                  className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg cursor-pointer hover:bg-zinc-700 transition-colors"
                  onClick={() => toggleAgentExpansion(agent.id)}
                >
                  <div className="flex items-center gap-3">
                    {expandedAgents.has(agent.id) ? 
                      <ChevronDown className="h-4 w-4 text-gray-400" /> :
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    }
                    {getAgentTypeIcon(agent.type)}
                    <div>
                      <div className="text-white font-medium flex items-center gap-2">
                        {agent.name}
                        {agent.metrics.efficiencyRating >= 90 && (
                          <Star className="h-3 w-3 text-yellow-400" />
                        )}
                      </div>
                      <div className="text-sm text-gray-400 flex items-center gap-2">
                        <span>{agent.type.toUpperCase()}</span>
                        <span>•</span>
                        <Activity className="h-3 w-3" />
                        <span>{agent.currentTasks.length} active</span>
                        {agent.currentWorkflow && (
                          <>
                            <span>•</span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleWorkflowClick(agent.currentWorkflow!);
                              }}
                              className="text-blue-400 hover:text-blue-300 flex items-center gap-1"
                            >
                              {agent.currentWorkflow}
                              <ExternalLink className="h-3 w-3" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge className={`${getStatusColor(agent.status)} text-white border-none text-xs`}>
                      {agent.status}
                    </Badge>
                    <div className="text-sm text-gray-400">
                      {agent.availability}%
                    </div>
                  </div>
                </div>

                {/* Agent Availability Bar */}
                <div className="px-3">
                  <Progress 
                    value={agent.availability} 
                    className="h-1"
                    style={{ background: 'rgb(39, 39, 42)' }}
                  />
                </div>

                {/* Expanded Agent Details */}
                {expandedAgents.has(agent.id) && (
                  <div className="ml-6 space-y-3 border-l-2 border-zinc-700 pl-4">
                    {/* Agent Metrics */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Efficiency</span>
                          <span className={`font-medium ${getEfficiencyColor(agent.metrics.efficiencyRating)}`}>
                            {agent.metrics.efficiencyRating}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Success Rate</span>
                          <span className="text-white font-medium">
                            {agent.metrics.successRate}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Workload</span>
                          <span className="text-white font-medium">
                            {agent.metrics.workloadScore}/100
                          </span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Completed Today</span>
                          <span className="text-green-400 font-medium">
                            {agent.completedTasksToday}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Avg. Time</span>
                          <span className="text-white font-medium">
                            {agent.metrics.averageCompletionTime}h
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Collaboration</span>
                          <span className="text-white font-medium">
                            {agent.metrics.collaborationScore}/10
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Current Tasks */}
                    {agent.currentTasks.length > 0 && (
                      <div className="text-sm">
                        <div className="font-medium text-white mb-2">
                          Current Tasks ({agent.currentTasks.length}):
                        </div>
                        <div className="space-y-2">
                          {agent.currentTasks.map((task) => (
                            <div 
                              key={task.id} 
                              className="flex items-center justify-between p-2 bg-zinc-800/50 rounded cursor-pointer hover:bg-zinc-800 transition-colors"
                              onClick={() => handleTaskClick(task, agent)}
                            >
                              <div className="flex items-center gap-2">
                                {getStatusIcon(task.status)}
                                <span className="text-xs text-gray-300">{task.name}</span>
                                <Badge variant="outline" className={`text-xs ${getPriorityColor(task.priority)}`}>
                                  {task.priority}
                                </Badge>
                                <Badge variant="outline" className="text-xs bg-purple-500/20 text-purple-400 border-purple-500/30">
                                  {task.type}
                                </Badge>
                                {task.workflowId && (
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleWorkflowClick(task.workflowId!);
                                    }}
                                    className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                  >
                                    <ExternalLink className="h-3 w-3" />
                                  </button>
                                )}
                              </div>
                              {task.estimatedDuration && (
                                <div className="text-xs text-gray-400">
                                  {task.actualDuration || 0}h / {task.estimatedDuration}h
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Specializations */}
                    {agent.specializations.length > 0 && (
                      <div className="text-sm">
                        <div className="font-medium text-white mb-1">Specializations:</div>
                        <div className="flex flex-wrap gap-1">
                          {agent.specializations.map((spec) => (
                            <Badge key={spec} variant="outline" className="text-xs bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                              {spec}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Collaboration */}
                    {agent.collaboratingWith && agent.collaboratingWith.length > 0 && (
                      <div className="text-sm">
                        <div className="font-medium text-white mb-1">Collaborating with:</div>
                        <div className="flex flex-wrap gap-1">
                          {agent.collaboratingWith.map((collaborator) => (
                            <Badge key={collaborator} variant="outline" className="text-xs bg-orange-500/20 text-orange-400 border-orange-500/30">
                              {collaborator}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Last Activity */}
                    <div className="text-xs text-gray-500 pt-2 border-t border-zinc-700">
                      <div className="flex items-center justify-between">
                        <span>Last activity: {new Date(agent.lastActivity).toLocaleString()}</span>
                        <div className="flex items-center gap-1">
                          <Activity className="h-3 w-3" />
                          <span>Live updates</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
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

      {/* Workflow Detail Modal */}
      <WorkflowDetailModal
        workflowId={selectedWorkflowId}
        isOpen={isWorkflowModalOpen}
        onClose={() => {
          setIsWorkflowModalOpen(false);
          setSelectedWorkflowId(null);
        }}
      />
    </>
  );
}; 