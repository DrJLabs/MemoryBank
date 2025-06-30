"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ChevronDown, 
  ChevronRight, 
  FileText, 
  Users, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  GitBranch,
  Target,
  Calendar,
  User,
  MessageSquare,
  Link,
  Tag
} from 'lucide-react';
import axios from 'axios';

interface Story {
  id: string;
  title: string;
  status: 'Draft' | 'Ready' | 'In Progress' | 'Review' | 'Done';
  agent?: string;
  workflow?: string;
  lastUpdated: string;
  description: string;
  acceptanceCriteria?: string[];
  tasks?: StoryTask[];
  dependencies?: string[];
  epicId?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  estimatedHours?: number;
  actualHours?: number;
  assignedTo?: string;
  tags?: string[];
}

interface Epic {
  id: string;
  title: string;
  status: 'Planning' | 'Active' | 'Complete' | 'On Hold';
  stories: string[];
  progress: number;
  description: string;
  startDate?: string;
  targetDate?: string;
  owner?: string;
  objectives?: string[];
  keyResults?: string[];
  dependencies?: string[];
  risks?: string[];
}

interface StoryTask {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'complete';
  agent: string;
  estimatedHours?: number;
  actualHours?: number;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'Done':
    case 'Complete': return <CheckCircle className="h-4 w-4 text-green-400" />;
    case 'In Progress':
    case 'Active': return <Clock className="h-4 w-4 text-blue-400" />;
    case 'Review': return <AlertCircle className="h-4 w-4 text-purple-400" />;
    case 'Ready': return <Target className="h-4 w-4 text-yellow-400" />;
    case 'On Hold': return <AlertCircle className="h-4 w-4 text-orange-400" />;
    default: return <FileText className="h-4 w-4 text-gray-400" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Done':
    case 'Complete': return 'bg-green-500';
    case 'In Progress':
    case 'Active': return 'bg-blue-500';
    case 'Review': return 'bg-purple-500';
    case 'Ready': return 'bg-yellow-500';
    case 'On Hold': return 'bg-orange-500';
    default: return 'bg-gray-500';
  }
};

const getPriorityColor = (priority?: string) => {
  switch (priority) {
    case 'critical': return 'text-red-400 border-red-500/30';
    case 'high': return 'text-orange-400 border-orange-500/30';
    case 'medium': return 'text-yellow-400 border-yellow-500/30';
    default: return 'text-gray-400 border-gray-500/30';
  }
};

export const StoryEpicTracker: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [epics, setEpics] = useState<Epic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState('stories');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try proxy paths first, fallback to direct
      let storiesResponse, epicsResponse;
      try {
        [storiesResponse, epicsResponse] = await Promise.all([
          axios.get('/api/bmad/stories/detailed', { timeout: 5000 }),
          axios.get('/api/bmad/epics/detailed', { timeout: 5000 })
        ]);
      } catch (proxyError) {
        console.warn('Proxy failed, trying direct connection:', proxyError);
        [storiesResponse, epicsResponse] = await Promise.all([
          axios.get('http://localhost:8767/api/v1/bmad/stories/detailed', { timeout: 5000 }),
          axios.get('http://localhost:8767/api/v1/bmad/epics/detailed', { timeout: 5000 })
        ]);
      }
      
      if (storiesResponse.data && Array.isArray(storiesResponse.data)) {
        setStories(storiesResponse.data);
      } else {
        setStories([]);
      }
      
      if (epicsResponse.data && Array.isArray(epicsResponse.data)) {
        setEpics(epicsResponse.data);
      } else {
        setEpics([]);
      }
      
      setError(null);
    } catch (err) {
      console.error('Story/Epic fetch error:', err);
      setError('Failed to fetch story and epic data');
      // Set empty arrays to prevent perpetual loading
      setStories([]);
      setEpics([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const toggleItemExpansion = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const getStoryProgress = (story: Story) => {
    if (!story.tasks || story.tasks.length === 0) {
      return story.status === 'Done' ? 100 : 0;
    }
    const completedTasks = story.tasks.filter(task => task.status === 'complete').length;
    return (completedTasks / story.tasks.length) * 100;
  };

  const getEpicStories = (epicId: string) => {
    return stories.filter(story => story.epicId === epicId);
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-400" />
            Stories & Epics
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

  if (error) {
    return (
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-red-400" />
            Stories & Epics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">{error}</div>
            <Button 
              onClick={fetchData}
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
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-400" />
          Stories & Epics
          <div className="ml-auto flex items-center gap-2">
            <Badge className="bg-blue-500 text-white">
              {stories.length} Stories
            </Badge>
            <Badge className="bg-purple-500 text-white">
              {epics.length} Epics
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-zinc-800">
            <TabsTrigger value="stories" className="data-[state=active]:bg-zinc-700">
              Stories ({stories.length})
            </TabsTrigger>
            <TabsTrigger value="epics" className="data-[state=active]:bg-zinc-700">
              Epics ({epics.length})
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="stories" className="space-y-4 max-h-96 overflow-y-auto">
            {stories.map((story) => (
              <div key={story.id} className="space-y-2">
                {/* Story Header */}
                <div 
                  className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg cursor-pointer hover:bg-zinc-700 transition-colors"
                  onClick={() => toggleItemExpansion(story.id)}
                >
                  <div className="flex items-center gap-3">
                    {expandedItems.has(story.id) ? 
                      <ChevronDown className="h-4 w-4 text-gray-400" /> :
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    }
                    {getStatusIcon(story.status)}
                    <div className="min-w-0 flex-1">
                      <div className="text-white font-medium truncate">{story.title}</div>
                      <div className="text-sm text-gray-400 flex items-center gap-2">
                        <span>{story.id}</span>
                        {story.agent && (
                          <>
                            <span>•</span>
                            <User className="h-3 w-3" />
                            <span>{story.agent}</span>
                          </>
                        )}
                        {story.epicId && (
                          <>
                            <span>•</span>
                            <Link className="h-3 w-3" />
                            <span>{story.epicId}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {story.priority && (
                      <Badge variant="outline" className={`text-xs ${getPriorityColor(story.priority)}`}>
                        {story.priority}
                      </Badge>
                    )}
                    <Badge className={`${getStatusColor(story.status)} text-white border-none`}>
                      {story.status}
                    </Badge>
                    <div className="text-sm text-gray-400">
                      {getStoryProgress(story).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Story Progress */}
                <div className="px-3">
                  <Progress 
                    value={getStoryProgress(story)} 
                    className="h-2"
                    style={{ background: 'rgb(39, 39, 42)' }}
                  />
                </div>

                {/* Expanded Story Details */}
                {expandedItems.has(story.id) && (
                  <div className="ml-6 space-y-3 border-l-2 border-zinc-700 pl-4">
                    {/* Story Description */}
                    <div className="text-sm text-gray-300">
                      <div className="font-medium text-white mb-1">Description:</div>
                      <div className="bg-zinc-800/50 p-2 rounded text-xs">
                        {story.description}
                      </div>
                    </div>

                    {/* Acceptance Criteria */}
                    {story.acceptanceCriteria && story.acceptanceCriteria.length > 0 && (
                      <div className="text-sm">
                        <div className="font-medium text-white mb-1">Acceptance Criteria:</div>
                        <div className="space-y-1">
                          {story.acceptanceCriteria.map((criteria, index) => (
                            <div key={index} className="flex items-start gap-2 text-xs text-gray-300">
                              <CheckCircle className="h-3 w-3 mt-0.5 text-green-400" />
                              <span>{criteria}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Story Tasks */}
                    {story.tasks && story.tasks.length > 0 && (
                      <div className="text-sm">
                        <div className="font-medium text-white mb-1">Tasks:</div>
                        <div className="space-y-1">
                          {story.tasks.map((task) => (
                            <div key={task.id} className="flex items-center justify-between p-2 bg-zinc-800/50 rounded">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(task.status)}
                                <span className="text-xs text-gray-300">{task.name}</span>
                                <Badge variant="outline" className="text-xs bg-green-500/20 text-green-400 border-green-500/30">
                                  {task.agent}
                                </Badge>
                              </div>
                              {task.estimatedHours && (
                                <div className="text-xs text-gray-400">
                                  {task.actualHours || 0}h / {task.estimatedHours}h
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Story Tags */}
                    {story.tags && story.tags.length > 0 && (
                      <div className="flex items-center gap-2">
                        <Tag className="h-3 w-3 text-gray-400" />
                        <div className="flex flex-wrap gap-1">
                          {story.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs bg-blue-500/20 text-blue-400 border-blue-500/30">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Story Metadata */}
                    <div className="text-xs text-gray-500 pt-2 border-t border-zinc-700">
                      <div className="flex items-center justify-between">
                        <span>Updated: {new Date(story.lastUpdated).toLocaleString()}</span>
                        {story.estimatedHours && (
                          <span>Estimated: {story.estimatedHours}h</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </TabsContent>

          <TabsContent value="epics" className="space-y-4 max-h-96 overflow-y-auto">
            {epics.map((epic) => {
              const epicStories = getEpicStories(epic.id);
              return (
                <div key={epic.id} className="space-y-2">
                  {/* Epic Header */}
                  <div 
                    className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg cursor-pointer hover:bg-zinc-700 transition-colors"
                    onClick={() => toggleItemExpansion(epic.id)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedItems.has(epic.id) ? 
                        <ChevronDown className="h-4 w-4 text-gray-400" /> :
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      }
                      {getStatusIcon(epic.status)}
                      <div className="min-w-0 flex-1">
                        <div className="text-white font-medium truncate">{epic.title}</div>
                        <div className="text-sm text-gray-400 flex items-center gap-2">
                          <span>{epic.id}</span>
                          {epic.owner && (
                            <>
                              <span>•</span>
                              <User className="h-3 w-3" />
                              <span>{epic.owner}</span>
                            </>
                          )}
                          <span>•</span>
                          <FileText className="h-3 w-3" />
                          <span>{epicStories.length} stories</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge className={`${getStatusColor(epic.status)} text-white border-none`}>
                        {epic.status}
                      </Badge>
                      <div className="text-sm text-gray-400">
                        {epic.progress.toFixed(0)}%
                      </div>
                    </div>
                  </div>

                  {/* Epic Progress */}
                  <div className="px-3">
                    <Progress 
                      value={epic.progress} 
                      className="h-2"
                      style={{ background: 'rgb(39, 39, 42)' }}
                    />
                  </div>

                  {/* Expanded Epic Details */}
                  {expandedItems.has(epic.id) && (
                    <div className="ml-6 space-y-3 border-l-2 border-zinc-700 pl-4">
                      {/* Epic Description */}
                      <div className="text-sm text-gray-300">
                        <div className="font-medium text-white mb-1">Description:</div>
                        <div className="bg-zinc-800/50 p-2 rounded text-xs">
                          {epic.description}
                        </div>
                      </div>

                      {/* Epic Objectives */}
                      {epic.objectives && epic.objectives.length > 0 && (
                        <div className="text-sm">
                          <div className="font-medium text-white mb-1">Objectives:</div>
                          <div className="space-y-1">
                            {epic.objectives.map((objective, index) => (
                              <div key={index} className="flex items-start gap-2 text-xs text-gray-300">
                                <Target className="h-3 w-3 mt-0.5 text-blue-400" />
                                <span>{objective}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Key Results */}
                      {epic.keyResults && epic.keyResults.length > 0 && (
                        <div className="text-sm">
                          <div className="font-medium text-white mb-1">Key Results:</div>
                          <div className="space-y-1">
                            {epic.keyResults.map((result, index) => (
                              <div key={index} className="flex items-start gap-2 text-xs text-gray-300">
                                <CheckCircle className="h-3 w-3 mt-0.5 text-green-400" />
                                <span>{result}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Epic Stories */}
                      {epicStories.length > 0 && (
                        <div className="text-sm">
                          <div className="font-medium text-white mb-1">Stories ({epicStories.length}):</div>
                          <div className="space-y-1">
                            {epicStories.map((story) => (
                              <div key={story.id} className="flex items-center justify-between p-2 bg-zinc-800/50 rounded">
                                <div className="flex items-center gap-2">
                                  {getStatusIcon(story.status)}
                                  <span className="text-xs text-gray-300">{story.title}</span>
                                </div>
                                <Badge className={`${getStatusColor(story.status)} text-white border-none text-xs`}>
                                  {story.status}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Epic Timeline */}
                      {(epic.startDate || epic.targetDate) && (
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {epic.startDate && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              <span>Started: {new Date(epic.startDate).toLocaleDateString()}</span>
                            </div>
                          )}
                          {epic.targetDate && (
                            <div className="flex items-center gap-1">
                              <Target className="h-3 w-3" />
                              <span>Target: {new Date(epic.targetDate).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}; 