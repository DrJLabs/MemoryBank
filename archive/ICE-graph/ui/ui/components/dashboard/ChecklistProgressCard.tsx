"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  ChevronDown, 
  ChevronRight, 
  CheckSquare, 
  Square,
  Check,
  X,
  Clock, 
  CheckCircle, 
  AlertCircle,
  User,
  Calendar,
  Target,
  Activity,
  ExternalLink,
  Filter
} from 'lucide-react';
import axios from 'axios';

interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
  completedBy?: string;
  completedAt?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'development' | 'testing' | 'documentation' | 'deployment' | 'review';
  estimatedMinutes?: number;
  actualMinutes?: number;
  dependencies: string[];
}

interface Checklist {
  id: string;
  name: string;
  description?: string;
  category: 'story' | 'epic' | 'sprint' | 'release' | 'quality-gate';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignedTo: string;
  dueDate?: string;
  items: ChecklistItem[];
  completedItems: number;
  totalItems: number;
  progress: number;
  status: 'not-started' | 'in-progress' | 'completed' | 'blocked';
  createdAt: string;
  lastUpdated: string;
  relatedStory?: string;
  relatedEpic?: string;
}

interface ChecklistProgressData {
  totalChecklists: number;
  completedChecklists: number;
  inProgressChecklists: number;
  blockedChecklists: number;
  overallProgress: number;
  itemsCompletedToday: number;
  averageCompletionTime: number;
  checklists: Checklist[];
  categoryBreakdown: {
    [key: string]: {
      total: number;
      completed: number;
      progress: number;
    };
  };
  recentlyCompleted: {
    checklistId: string;
    checklistName: string;
    itemText: string;
    completedBy: string;
    completedAt: string;
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

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'development': return 'bg-blue-500';
    case 'testing': return 'bg-green-500';
    case 'documentation': return 'bg-purple-500';
    case 'deployment': return 'bg-red-500';
    case 'review': return 'bg-yellow-500';
    default: return 'bg-gray-500';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return <CheckCircle className="h-4 w-4 text-green-400" />;
    case 'in-progress': return <Clock className="h-4 w-4 text-blue-400" />;
    case 'blocked': return <AlertCircle className="h-4 w-4 text-red-400" />;
    default: return <Square className="h-4 w-4 text-gray-400" />;
  }
};

export const ChecklistProgressCard: React.FC = () => {
  const [checklistData, setChecklistData] = useState<ChecklistProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [selectedView, setSelectedView] = useState<'overview' | 'checklists' | 'recent'>('overview');
  const [expandedChecklists, setExpandedChecklists] = useState<Set<string>>(new Set());
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const fetchChecklistData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/bmad/checklists/progress', { timeout: 5000 });
      
      if (response.data) {
        setChecklistData(response.data);
      } else {
        throw new Error("No data received");
      }
    } catch (err) {
      console.error('Checklist fetch error:', err);
      setError('Failed to fetch checklist data');
      setChecklistData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChecklistData();
    const interval = setInterval(fetchChecklistData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const toggleChecklistExpansion = (checklistId: string) => {
    const newExpanded = new Set(expandedChecklists);
    if (newExpanded.has(checklistId)) {
      newExpanded.delete(checklistId);
    } else {
      newExpanded.add(checklistId);
    }
    setExpandedChecklists(newExpanded);
  };

  const getFilteredChecklists = () => {
    if (!checklistData) return [];
    
    return checklistData.checklists.filter(checklist => {
      const categoryMatch = filterCategory === 'all' || checklist.category === filterCategory;
      const statusMatch = filterStatus === 'all' || checklist.status === filterStatus;
      return categoryMatch && statusMatch;
    });
  };

  const handleItemToggle = async (checklistId: string, itemId: string, completed: boolean) => {
    try {
        await axios.patch(`/api/bmad/checklists/${checklistId}/items/${itemId}`, { completed: !completed });
        fetchChecklistData();
    } catch (err) {
        console.error('Failed to toggle checklist item', err);
        setError('Failed to update item. Please try again.');
    }
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-green-400" />
            Checklist Progress
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

  if (error || !checklistData) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-red-400" />
            Checklist Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">
              {error || 'No checklist data available'}
            </div>
            <Button 
              onClick={fetchChecklistData}
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
    <Card className="bg-zinc-900 border-zinc-800">
      <CardHeader 
        className="cursor-pointer hover:bg-zinc-800 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <CardTitle className="text-white flex items-center gap-2">
          {expanded ? <ChevronDown className="h-4 w-4 text-gray-400" /> : <ChevronRight className="h-4 w-4 text-gray-400" />}
          <CheckSquare className="h-5 w-5 text-green-400" />
          Checklist Progress
          <div className="ml-auto flex items-center gap-2">
            <Badge className="bg-green-500 text-white">
              {checklistData.completedChecklists}/{checklistData.totalChecklists}
            </Badge>
            <Badge className="bg-blue-500 text-white">
              {checklistData.itemsCompletedToday} Today
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Overall Progress</span>
            <span className="text-white font-medium">{checklistData.overallProgress.toFixed(1)}%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">In Progress</span>
            <span className="text-white font-medium">{checklistData.inProgressChecklists}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Avg. Time</span>
            <span className="text-white font-medium">{checklistData.averageCompletionTime}h</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Blocked</span>
            <span className="text-red-400 font-medium">{checklistData.blockedChecklists}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1">
          <Progress value={checklistData.overallProgress} className="h-2" />
          <div className="flex justify-between text-xs text-gray-400">
            <span>{checklistData.completedChecklists} completed</span>
            <span>{checklistData.totalChecklists - checklistData.completedChecklists} remaining</span>
          </div>
        </div>

        {/* Expanded Details */}
        {expanded && (
          <div className="space-y-4 border-t border-zinc-700 pt-4">
            {/* View Controls */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">View:</span>
              {(['overview', 'checklists', 'recent'] as const).map((view) => (
                <Button
                  key={view}
                  size="sm"
                  variant={selectedView === view ? "default" : "outline"}
                  className={`text-xs ${
                    selectedView === view 
                      ? 'bg-green-500 text-white' 
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
                {/* Category Breakdown */}
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Category Breakdown</h4>
                  <div className="space-y-2">
                    {Object.entries(checklistData.categoryBreakdown).map(([category, stats]) => (
                      <div key={category} className="flex items-center justify-between p-2 bg-zinc-800 rounded text-xs">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getCategoryColor(category)}`}></div>
                          <span className="text-gray-300 capitalize">{category}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-gray-400">{stats.completed}/{stats.total}</span>
                          <span className="text-white font-medium">{stats.progress.toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Checklists */}
            {selectedView === 'checklists' && (
              <div className="space-y-4">
                {/* Filters */}
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-gray-400" />
                  <select 
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs text-white"
                  >
                    <option value="all">All Categories</option>
                    <option value="story">Story</option>
                    <option value="epic">Epic</option>
                    <option value="sprint">Sprint</option>
                    <option value="release">Release</option>
                  </select>
                  <select 
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs text-white"
                  >
                    <option value="all">All Status</option>
                    <option value="not-started">Not Started</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>

                {/* Checklist List */}
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {getFilteredChecklists().map((checklist) => (
                    <div key={checklist.id} className="space-y-2">
                      {/* Checklist Header */}
                      <div 
                        className="flex items-center justify-between p-2 bg-zinc-800 rounded cursor-pointer hover:bg-zinc-700 transition-colors"
                        onClick={() => toggleChecklistExpansion(checklist.id)}
                      >
                        <div className="flex items-center gap-2">
                          {expandedChecklists.has(checklist.id) ? 
                            <ChevronDown className="h-3 w-3 text-gray-400" /> :
                            <ChevronRight className="h-3 w-3 text-gray-400" />
                          }
                          {getStatusIcon(checklist.status)}
                          <span className="text-sm text-white">{checklist.name}</span>
                          <Badge variant="outline" className={`text-xs ${getPriorityColor(checklist.priority).replace('bg-', 'text-').replace('500', '400')} border-none`}>
                            {checklist.priority}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{checklist.completedItems}/{checklist.totalItems}</span>
                          <span className="text-xs text-white">{checklist.progress}%</span>
                        </div>
                      </div>

                      {/* Expanded Checklist Items */}
                      {expandedChecklists.has(checklist.id) && (
                        <div className="ml-4 space-y-1">
                          {checklist.items.map((item) => (
                            <div key={item.id} className="flex items-center justify-between p-2 bg-zinc-900 rounded text-xs">
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleItemToggle(checklist.id, item.id, item.completed);
                                  }}
                                  className="flex-shrink-0"
                                >
                                  {item.completed ? (
                                    <CheckSquare className="h-3 w-3 text-green-400" />
                                  ) : (
                                    <Square className="h-3 w-3 text-gray-400 hover:text-white" />
                                  )}
                                </button>
                                <span className={`text-gray-300 ${item.completed ? 'line-through opacity-75' : ''}`}>
                                  {item.text}
                                </span>
                                <Badge variant="outline" className={`text-xs ${getCategoryColor(item.category).replace('bg-', 'text-').replace('500', '400')} border-none`}>
                                  {item.category}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-2">
                                {item.completedBy && (
                                  <span className="text-gray-500">{item.completedBy}</span>
                                )}
                                {item.estimatedMinutes && (
                                  <span className="text-gray-400">{item.estimatedMinutes}m</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {selectedView === 'recent' && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Recently Completed ({checklistData.recentlyCompleted.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {checklistData.recentlyCompleted.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-zinc-800 rounded text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-400" />
                        <span className="text-gray-300">{item.itemText}</span>
                        <span className="text-gray-500">in {item.checklistName}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">{item.completedBy}</span>
                        <span className="text-gray-500">{new Date(item.completedAt).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Updated */}
            <div className="text-xs text-gray-500 text-center pt-2 border-t border-zinc-700">
              Last updated: {new Date().toLocaleTimeString()} • Auto-refresh every 30 seconds
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 