"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  ChevronDown, 
  ChevronRight, 
  GitBranch, 
  Users, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  FileText,
  Settings,
  Play,
  Pause,
  Square,
  ExternalLink,
  ChevronsRight,
  XCircle
} from 'lucide-react';
import { WorkflowDetailModal } from './WorkflowDetailModal';
import axios from 'axios';

interface WorkflowStage {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  agent?: string;
  tasks: WorkflowTask[];
  startTime?: string;
  endTime?: string;
}

interface WorkflowTask {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  agent: string;
  description?: string;
  checklist?: string[];
  dependencies?: string[];
}

interface Workflow {
  id: string;
  name: string;
  type: 'epic' | 'story' | 'task' | 'custom';
  currentStage: string;
  stages: WorkflowStage[];
  progress: number;
  status: 'active' | 'paused' | 'complete' | 'error';
  startTime: string;
  lastUpdated: string;
  assignedAgents: string[];
  metadata?: {
    storyId?: string;
    epicId?: string;
    priority?: 'low' | 'medium' | 'high' | 'critical';
  };
  last_run: string;
  current_stage?: string;
}

const getStatusIcon = (status: Workflow['status']) => {
  switch (status) {
    case 'success':
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'failed':
      return <XCircle className="h-5 w-5 text-red-500" />;
    case 'in_progress':
      return <Clock className="h-5 w-5 text-blue-500 animate-pulse" />;
    default:
      return <ChevronsRight className="h-5 w-5 text-gray-400" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'complete': return 'bg-green-500';
    case 'active': return 'bg-blue-500';
    case 'error': return 'bg-red-500';
    case 'paused': return 'bg-yellow-500';
    default: return 'bg-gray-500';
  }
};

const getWorkflowTypeIcon = (type: string) => {
  switch (type) {
    case 'epic': return <FileText className="h-4 w-4 text-purple-400" />;
    case 'story': return <GitBranch className="h-4 w-4 text-blue-400" />;
    case 'task': return <Settings className="h-4 w-4 text-green-400" />;
    default: return <GitBranch className="h-4 w-4 text-gray-400" />;
  }
};

export const WorkflowTracker: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedWorkflows, setExpandedWorkflows] = useState<Set<string>>(new Set());
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/bmad/workflows/detailed', { timeout: 5000 });
      
      if (response.data && Array.isArray(response.data)) {
        setWorkflows(response.data);
        setError(null);
      } else {
        setWorkflows([]);
        setError('No workflow data available');
      }
    } catch (err) {
      console.error('Workflow fetch error:', err);
      setError('Failed to fetch workflow data');
      // Set empty array to prevent perpetual loading
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
    const interval = setInterval(fetchWorkflows, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const toggleWorkflowExpansion = (workflowId: string) => {
    const newExpanded = new Set(expandedWorkflows);
    if (newExpanded.has(workflowId)) {
      newExpanded.delete(workflowId);
    } else {
      newExpanded.add(workflowId);
    }
    setExpandedWorkflows(newExpanded);
  };

  const toggleStageExpansion = (stageId: string) => {
    const newExpanded = new Set(expandedStages);
    if (newExpanded.has(stageId)) {
      newExpanded.delete(stageId);
    } else {
      newExpanded.add(stageId);
    }
    setExpandedStages(newExpanded);
  };

  const handleWorkflowAction = async (workflowId: string, action: 'pause' | 'resume' | 'stop') => {
    try {
      const response = await axios.post(`/api/bmad/workflows/${workflowId}/${action}`, {}, { timeout: 5000 });
      if (!response.data) {
        throw new Error('No response data');
      }
      fetchWorkflows(); // Refresh data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      console.error(`Failed to ${action} workflow:`, errorMessage);
      setError(`Operation failed: ${errorMessage}`);
    }
  };

  const handleWorkflowNameClick = (workflowId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedWorkflowId(workflowId);
    setIsDetailModalOpen(true);
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-purple-400" />
            Active Workflows
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || workflows.length === 0) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-red-400" />
            Active Workflows
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">
              {error || 'No active workflows found. Check the console for errors.'}
            </div>
            <Button 
              onClick={fetchWorkflows}
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
            <GitBranch className="h-5 w-5 text-purple-400" />
            Active Workflows
            <Badge className="ml-auto bg-purple-500 text-white">
              {workflows.filter(w => w.status === 'active').length} Active
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 max-h-96 overflow-y-auto">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="space-y-2">
              {/* Workflow Header */}
              <div 
                className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg cursor-pointer hover:bg-zinc-700 transition-colors"
                onClick={() => toggleWorkflowExpansion(workflow.id)}
              >
                <div className="flex items-center gap-3">
                  {expandedWorkflows.has(workflow.id) ? 
                    <ChevronDown className="h-4 w-4 text-gray-400" /> :
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  }
                  {getWorkflowTypeIcon(workflow.type)}
                  <div>
                    <div className="text-white font-medium flex items-center gap-2">
                      <span
                        className="hover:text-blue-400 transition-colors"
                        onClick={(e) => handleWorkflowNameClick(workflow.id, e)}
                      >
                        {workflow.name}
                      </span>
                      <ExternalLink 
                        className="h-3 w-3 text-gray-400 hover:text-blue-400 cursor-pointer"
                        onClick={(e) => handleWorkflowNameClick(workflow.id, e)}
                      />
                    </div>
                    <div className="text-sm text-gray-400">
                      {workflow.currentStage} • {workflow.assignedAgents.join(', ')}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Badge className={`${getStatusColor(workflow.status)} text-white border-none`}>
                    {workflow.status}
                  </Badge>
                  <div className="text-sm text-gray-400">
                    {workflow.progress.toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Workflow Progress */}
              <div className="px-3">
                <Progress 
                  value={workflow.progress} 
                  className="h-2"
                  style={{ background: 'rgb(39, 39, 42)' }}
                />
              </div>

              {/* Expanded Workflow Details */}
              {expandedWorkflows.has(workflow.id) && (
                <div className="ml-6 space-y-3 border-l-2 border-zinc-700 pl-4">
                  {/* Workflow Controls */}
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-white hover:bg-zinc-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleWorkflowAction(workflow.id, workflow.status === 'active' ? 'pause' : 'resume');
                      }}
                    >
                      {workflow.status === 'active' ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                      {workflow.status === 'active' ? 'Pause' : 'Resume'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-red-400 hover:bg-red-900/20"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleWorkflowAction(workflow.id, 'stop');
                      }}
                    >
                      <Square className="h-3 w-3" />
                      Stop
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-blue-400 hover:bg-blue-900/20"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleWorkflowNameClick(workflow.id, e);
                      }}
                    >
                      <ExternalLink className="h-3 w-3" />
                      View Details
                    </Button>
                  </div>

                  {/* Workflow Stages */}
                  {workflow.stages.map((stage, index) => (
                    <div key={stage.id} className="space-y-2">
                      {/* Stage Header */}
                      <div 
                        className="flex items-center justify-between p-2 bg-zinc-800/50 rounded cursor-pointer hover:bg-zinc-800 transition-colors"
                        onClick={() => toggleStageExpansion(stage.id)}
                      >
                        <div className="flex items-center gap-2">
                          {expandedStages.has(stage.id) ? 
                            <ChevronDown className="h-3 w-3 text-gray-400" /> :
                            <ChevronRight className="h-3 w-3 text-gray-400" />
                          }
                          {getStatusIcon(stage.status)}
                          <span className="text-sm text-white">{stage.name}</span>
                          {stage.agent && (
                            <Badge variant="outline" className="text-xs bg-blue-500/20 text-blue-400 border-blue-500/30">
                              {stage.agent}
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs text-gray-400">
                          {stage.tasks.length} tasks
                        </div>
                      </div>

                      {/* Expanded Stage Details */}
                      {expandedStages.has(stage.id) && (
                        <div className="ml-4 space-y-2">
                          {stage.tasks.map((task) => (
                            <div key={task.id} className="flex items-center justify-between p-2 bg-zinc-900/50 rounded">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(task.status)}
                                <span className="text-sm text-gray-300">{task.name}</span>
                                <Badge variant="outline" className="text-xs bg-green-500/20 text-green-400 border-green-500/30">
                                  {task.agent}
                                </Badge>
                              </div>
                              {task.checklist && (
                                <div className="text-xs text-gray-400">
                                  {task.checklist.filter(item => item.includes('✓')).length}/{task.checklist.length} complete
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Workflow Metadata */}
                  {workflow.metadata && (
                    <div className="text-xs text-gray-500 pt-2 border-t border-zinc-700">
                      <div className="flex items-center justify-between">
                        <span>Started: {new Date(workflow.startTime).toLocaleString()}</span>
                        {workflow.metadata.priority && (
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${
                              workflow.metadata.priority === 'critical' ? 'text-red-400 border-red-500/30' :
                              workflow.metadata.priority === 'high' ? 'text-orange-400 border-orange-500/30' :
                              workflow.metadata.priority === 'medium' ? 'text-yellow-400 border-yellow-500/30' :
                              'text-gray-400 border-gray-500/30'
                            }`}
                          >
                            {workflow.metadata.priority}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Workflow Detail Modal */}
      <WorkflowDetailModal
        workflowId={selectedWorkflowId}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedWorkflowId(null);
        }}
      />
    </>
  );
}; 