"use client";

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  GitBranch,
  Clock,
  Users,
  PlayCircle,
  PauseCircle,
  StopCircle,
  CheckCircle2,
  Circle,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Activity,
  ListChecks
} from 'lucide-react';
import axios from 'axios';

interface WorkflowTask {
  id: string;
  name: string;
  status: string;
  agent: string;
  description?: string;
  checklist?: string[];
  dependencies?: string[];
}

interface WorkflowStage {
  id: string;
  name: string;
  status: string;
  agent?: string;
  tasks: WorkflowTask[];
  startTime?: string;
  endTime?: string;
}

interface WorkflowDetail {
  id: string;
  name: string;
  type: string;
  currentStage: string;
  stages: WorkflowStage[];
  progress: number;
  status: string;
  startTime: string;
  lastUpdated: string;
  assignedAgents: string[];
  metadata?: any;
}

interface WorkflowDetailModalProps {
  workflowId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

const getStageStatusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case 'complete': return <CheckCircle2 className="h-4 w-4 text-green-400" />;
    case 'active': return <Activity className="h-4 w-4 text-blue-400 animate-pulse" />;
    case 'pending': return <Circle className="h-4 w-4 text-gray-400" />;
    case 'error': return <AlertCircle className="h-4 w-4 text-red-400" />;
    default: return <Circle className="h-4 w-4 text-gray-400" />;
  }
};

const getTaskStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'complete': return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'active': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
    default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  }
};

export const WorkflowDetailModal: React.FC<WorkflowDetailModalProps> = ({ workflowId, isOpen, onClose }) => {
  const [workflow, setWorkflow] = useState<WorkflowDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (workflowId && isOpen) {
      fetchWorkflowDetails();
    }
  }, [workflowId, isOpen]);

  const fetchWorkflowDetails = async () => {
    if (!workflowId) return;
    
    setLoading(true);
    try {
      // Try proxy path first, fallback to direct
      let response;
      try {
        response = await axios.get('/api/bmad/workflows/detailed');
      } catch (proxyError) {
        console.warn('Proxy failed, trying direct connection:', proxyError);
        response = await axios.get('http://localhost:8767/api/v1/bmad/workflows/detailed');
      }
      const workflowData = response.data.find((wf: WorkflowDetail) => wf.id === workflowId);
      if (workflowData) {
        setWorkflow(workflowData);
        // Expand the current stage by default
        setExpandedStages(new Set([workflowData.stages.find(s => s.name === workflowData.currentStage)?.id || '']));
      }
    } catch (error) {
      console.error('Failed to fetch workflow details:', error);
    } finally {
      setLoading(false);
    }
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

  const handleWorkflowAction = async (action: 'pause' | 'resume' | 'stop') => {
    if (!workflow) return;
    
    try {
      // Try proxy path first, fallback to direct
      try {
        await axios.post(`/api/bmad/workflows/${workflow.id}/${action}`);
      } catch (proxyError) {
        console.warn('Proxy failed, trying direct connection:', proxyError);
        await axios.post(`http://localhost:8767/api/v1/bmad/workflows/${workflow.id}/${action}`);
      }
      // Refresh workflow data
      fetchWorkflowDetails();
    } catch (error) {
      console.error(`Failed to ${action} workflow:`, error);
    }
  };

  if (!workflow && !loading) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-zinc-900 border-zinc-800 text-white max-w-4xl max-h-[80vh] overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
          </div>
        ) : workflow ? (
          <>
            <DialogHeader>
              <DialogTitle className="text-xl font-bold flex items-center gap-3">
                <GitBranch className="h-5 w-5 text-green-400" />
                {workflow.name}
              </DialogTitle>
              <DialogDescription className="text-gray-400 space-y-1">
                <div>Type: {workflow.type} • Current Stage: {workflow.currentStage}</div>
                <div className="text-xs">Last updated: {new Date(workflow.lastUpdated).toLocaleString()}</div>
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 mt-4">
              {/* Progress and Status */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Badge className={`${workflow.status === 'complete' ? 'bg-green-500' : 'bg-blue-500'} text-white border-none`}>
                      {workflow.status.toUpperCase()}
                    </Badge>
                    <span className="text-sm text-gray-400">
                      Started: {new Date(workflow.startTime).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-white hover:bg-zinc-700"
                      onClick={() => handleWorkflowAction('pause')}
                      disabled={workflow.status !== 'active'}
                    >
                      <PauseCircle className="h-4 w-4 mr-1" />
                      Pause
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-white hover:bg-zinc-700"
                      onClick={() => handleWorkflowAction('resume')}
                      disabled={workflow.status === 'active' || workflow.status === 'complete'}
                    >
                      <PlayCircle className="h-4 w-4 mr-1" />
                      Resume
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="bg-zinc-800 border-zinc-700 text-red-400 hover:bg-zinc-700"
                      onClick={() => handleWorkflowAction('stop')}
                      disabled={workflow.status === 'complete'}
                    >
                      <StopCircle className="h-4 w-4 mr-1" />
                      Stop
                    </Button>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Overall Progress</span>
                    <span className="text-white font-medium">{Math.round(workflow.progress)}%</span>
                  </div>
                  <Progress value={workflow.progress} className="h-2" />
                </div>
              </div>

              {/* Assigned Agents */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-gray-400">
                  <Users className="h-4 w-4" />
                  <span className="text-sm">Assigned Agents</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {workflow.assignedAgents.map((agent) => (
                    <Badge key={agent} variant="outline" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                      {agent}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Workflow Stages */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                  <ListChecks className="h-4 w-4" />
                  Workflow Stages ({workflow.stages.length})
                </h4>
                <div className="space-y-2">
                  {workflow.stages.map((stage, index) => (
                    <div key={stage.id} className="border border-zinc-700 rounded-lg overflow-hidden">
                      {/* Stage Header */}
                      <div 
                        className={`p-3 cursor-pointer hover:bg-zinc-800 transition-colors ${
                          stage.name === workflow.currentStage ? 'bg-zinc-800' : 'bg-zinc-900'
                        }`}
                        onClick={() => toggleStageExpansion(stage.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {expandedStages.has(stage.id) ? 
                              <ChevronDown className="h-4 w-4 text-gray-400" /> :
                              <ChevronRight className="h-4 w-4 text-gray-400" />
                            }
                            {getStageStatusIcon(stage.status)}
                            <span className="font-medium text-white">
                              Stage {index + 1}: {stage.name}
                            </span>
                            {stage.name === workflow.currentStage && (
                              <Badge className="bg-blue-500 text-white border-none text-xs">
                                CURRENT
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {stage.agent && (
                              <Badge variant="outline" className="text-xs bg-purple-500/20 text-purple-400 border-purple-500/30">
                                {stage.agent}
                              </Badge>
                            )}
                            <span className="text-sm text-gray-400">
                              {stage.tasks.length} tasks
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Stage Tasks (Expanded) */}
                      {expandedStages.has(stage.id) && (
                        <div className="p-3 bg-zinc-800/50 space-y-2">
                          {stage.tasks.map((task) => (
                            <div key={task.id} className="flex items-start gap-3 p-2 bg-zinc-900 rounded">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium text-white">{task.name}</span>
                                  <Badge variant="outline" className={`text-xs ${getTaskStatusColor(task.status)}`}>
                                    {task.status}
                                  </Badge>
                                </div>
                                {task.description && (
                                  <p className="text-xs text-gray-400 mt-1">{task.description}</p>
                                )}
                                <div className="flex items-center gap-4 mt-2">
                                  <span className="text-xs text-gray-500">Agent: {task.agent}</span>
                                  {task.dependencies && task.dependencies.length > 0 && (
                                    <span className="text-xs text-gray-500">
                                      Dependencies: {task.dependencies.join(', ')}
                                    </span>
                                  )}
                                </div>
                                {task.checklist && task.checklist.length > 0 && (
                                  <div className="mt-2 text-xs text-gray-400">
                                    <span className="flex items-center gap-1">
                                      <ListChecks className="h-3 w-3" />
                                      {task.checklist.length} checklist items
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                          {stage.startTime && (
                            <div className="text-xs text-gray-500 pt-2 border-t border-zinc-700">
                              <div className="flex items-center justify-between">
                                <span>Started: {new Date(stage.startTime).toLocaleString()}</span>
                                {stage.endTime && (
                                  <span>Completed: {new Date(stage.endTime).toLocaleString()}</span>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Metadata */}
              {workflow.metadata && Object.keys(workflow.metadata).length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-400">Metadata</h4>
                  <div className="bg-zinc-800 p-3 rounded-lg">
                    <pre className="text-xs text-gray-300 overflow-x-auto">
                      {JSON.stringify(workflow.metadata, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}; 