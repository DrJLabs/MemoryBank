"use client";

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Clock, 
  User, 
  Calendar,
  CheckCircle,
  AlertCircle,
  Target,
  FileText,
  GitBranch,
  Activity
} from 'lucide-react';

interface TaskDetail {
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
  agent?: string;
  description?: string;
  acceptanceCriteria?: string[];
  dependencies?: string[];
  progress?: number;
}

interface TaskDetailModalProps {
  task: TaskDetail | null;
  isOpen: boolean;
  onClose: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'complete': return 'bg-green-500';
    case 'active': return 'bg-blue-500';
    case 'error': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'bg-red-500 text-white';
    case 'high': return 'bg-orange-500 text-white';
    case 'medium': return 'bg-yellow-500 text-white';
    default: return 'bg-gray-500 text-white';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'story': return <FileText className="h-4 w-4" />;
    case 'epic': return <Target className="h-4 w-4" />;
    case 'workflow': return <GitBranch className="h-4 w-4" />;
    case 'checklist': return <CheckCircle className="h-4 w-4" />;
    default: return <Activity className="h-4 w-4" />;
  }
};

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({ task, isOpen, onClose }) => {
  if (!task) return null;

  const progress = task.actualDuration && task.estimatedDuration 
    ? Math.min((task.actualDuration / task.estimatedDuration) * 100, 100)
    : 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-zinc-900 border-zinc-800 text-white max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold flex items-center gap-3">
            {getTypeIcon(task.type)}
            {task.name}
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Task ID: {task.id}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Status and Priority */}
          <div className="flex items-center gap-4">
            <Badge className={`${getStatusColor(task.status)} text-white border-none`}>
              {task.status.toUpperCase()}
            </Badge>
            <Badge className={`${getPriorityColor(task.priority)} border-none`}>
              {task.priority.toUpperCase()} PRIORITY
            </Badge>
            <Badge variant="outline" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
              {task.type.toUpperCase()}
            </Badge>
          </div>

          {/* Time Information */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-400">
                <Calendar className="h-4 w-4" />
                <span className="text-sm">Started</span>
              </div>
              <p className="text-white">
                {task.startTime ? new Date(task.startTime).toLocaleString() : 'Not started'}
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-400">
                <Clock className="h-4 w-4" />
                <span className="text-sm">Duration</span>
              </div>
              <p className="text-white">
                {task.actualDuration || 0}h / {task.estimatedDuration || 0}h estimated
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          {task.estimatedDuration && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Progress</span>
                <span className="text-white">{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}

          {/* Agent Assignment */}
          {task.agent && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-400">
                <User className="h-4 w-4" />
                <span className="text-sm">Assigned Agent</span>
              </div>
              <p className="text-white capitalize">{task.agent}</p>
            </div>
          )}

          {/* Related IDs */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-400">Related Items</h4>
            <div className="flex flex-wrap gap-2">
              {task.storyId && (
                <Badge variant="outline" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                  Story: {task.storyId}
                </Badge>
              )}
              {task.epicId && (
                <Badge variant="outline" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                  Epic: {task.epicId}
                </Badge>
              )}
              {task.workflowId && (
                <Badge variant="outline" className="bg-green-500/20 text-green-400 border-green-500/30">
                  Workflow: {task.workflowId}
                </Badge>
              )}
            </div>
          </div>

          {/* Description */}
          {task.description && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-400">Description</h4>
              <p className="text-white text-sm bg-zinc-800 p-3 rounded-lg">{task.description}</p>
            </div>
          )}

          {/* Acceptance Criteria */}
          {task.acceptanceCriteria && task.acceptanceCriteria.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-400">Acceptance Criteria</h4>
              <ul className="space-y-1">
                {task.acceptanceCriteria.map((criteria, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-white">
                    <CheckCircle className="h-4 w-4 text-green-400 mt-0.5" />
                    <span>{criteria}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Dependencies */}
          {task.dependencies && task.dependencies.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-400">Dependencies</h4>
              <div className="flex flex-wrap gap-2">
                {task.dependencies.map((dep, index) => (
                  <Badge key={index} variant="outline" className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                    {dep}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Status Indicator */}
          {task.status === 'error' && (
            <div className="flex items-center gap-2 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <span className="text-red-400 text-sm">This task has encountered an error</span>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}; 