"""
BMAD Memory Integration Service

Enhanced memory integration specifically designed for BMAD operations,
leveraging the existing advanced memory system with BMAD-specific
categorization, context enrichment, and intelligent pattern recognition.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bmad_models import (
    BMadAgent, BMadWorkflow, BMadTask, BMadMemoryIntegration
)


class BMadMemoryIntegrationService:
    """
    Enhanced memory integration service for BMAD operations.
    
    Provides intelligent memory context retrieval, pattern recognition,
    and automated memory creation for BMAD workflows, agents, and tasks.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory_api_url = settings.MEMORY_BANK_API_URL
        self.headers = {"Content-Type": "application/json"}
        
        # BMAD-specific memory categories
        self.bmad_categories = {
            'AGENT_CONTEXT': {
                'description': 'Agent activation patterns and operational context',
                'keywords': ['agent', 'activate', 'context', 'performance', 'specialization'],
                'relevance_weight': 1.0
            },
            'WORKFLOW_PATTERNS': {
                'description': 'Successful workflow execution patterns and optimizations',
                'keywords': ['workflow', 'pattern', 'sequence', 'optimization', 'stage'],
                'relevance_weight': 0.9
            },
            'TASK_COMPLETION': {
                'description': 'Task execution insights and quality improvements',
                'keywords': ['task', 'completion', 'quality', 'duration', 'output'],
                'relevance_weight': 0.8
            },
            'AGENT_COLLABORATION': {
                'description': 'Multi-agent collaboration effectiveness and patterns',
                'keywords': ['collaboration', 'handoff', 'team', 'coordination', 'communication'],
                'relevance_weight': 0.7
            },
            'WORKFLOW_OPTIMIZATION': {
                'description': 'Performance improvements and workflow optimizations',
                'keywords': ['optimization', 'performance', 'improvement', 'efficiency', 'bottleneck'],
                'relevance_weight': 0.8
            },
            'QUALITY_METRICS': {
                'description': 'Quality scores, feedback, and improvement insights',
                'keywords': ['quality', 'metrics', 'feedback', 'improvement', 'standards'],
                'relevance_weight': 0.6
            },
            'USER_PREFERENCES': {
                'description': 'User-specific preferences for workflows and agents',
                'keywords': ['preference', 'user', 'configuration', 'customization', 'settings'],
                'relevance_weight': 0.7
            },
            'AGENT_SESSIONS': {
                'description': 'Agent session summaries and handoff information',
                'keywords': ['session', 'summary', 'handoff', 'state', 'transition'],
                'relevance_weight': 0.6
            }
        }
    
    # =============================================
    # AGENT MEMORY INTEGRATION
    # =============================================
    
    def get_agent_activation_context(self, agent_id: str, user_id: str, 
                                   session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get comprehensive memory context for agent activation.
        
        Retrieves relevant memories for agent activation including:
        - Agent-specific patterns and preferences
        - Recent successful activations
        - User preferences for this agent
        - Workflow context if available
        """
        
        # Build context-aware search queries
        search_queries = [
            f"AGENT_CONTEXT {agent_id} activation patterns preferences",
            f"USER_PREFERENCES {user_id} agent {agent_id} configuration",
            f"AGENT_SESSIONS {agent_id} successful handoff quality"
        ]
        
        # Add workflow context if available
        if session_context and session_context.get('workflow_type'):
            workflow_type = session_context['workflow_type']
            search_queries.append(f"WORKFLOW_PATTERNS {workflow_type} {agent_id} optimization")
        
        # Execute memory searches
        all_memories = []
        search_metadata = []
        
        for query in search_queries:
            memories = self._search_memories(query, user_id, limit=5)
            all_memories.extend(memories.get('items', []))
            search_metadata.append({
                'query': query,
                'count': len(memories.get('items', [])),
                'relevance': memories.get('average_relevance', 0)
            })
        
        # Enhance with related memories
        enhanced_memories = self._get_related_memories(all_memories, user_id)
        
        # Calculate context scores
        context_scores = self._calculate_context_scores(enhanced_memories, agent_id)
        
        # Store memory integration record
        integration_record = self._create_memory_integration_record(
            'agent', None, 'AGENT_CONTEXT', 'activation', 
            enhanced_memories, context_scores
        )
        
        return {
            'memories': enhanced_memories,
            'context_scores': context_scores,
            'search_metadata': search_metadata,
            'categories': list(set([m.get('category', 'GENERAL') for m in enhanced_memories])),
            'total_memories': len(enhanced_memories),
            'integration_id': str(integration_record.id) if integration_record else None,
            'activation_insights': self._extract_activation_insights(enhanced_memories, agent_id)
        }
    
    def store_agent_activation_memory(self, agent: BMadAgent, user_id: str, 
                                    session_id: str, context_used: Dict[str, Any]) -> bool:
        """Store agent activation memory with rich context."""
        
        # Create structured memory content
        memory_content = self._format_agent_activation_memory(agent, context_used)
        
        # Store in memory system
        memory_result = self._store_memory(
            user_id, memory_content, 'AGENT_CONTEXT',
            {
                'agent_id': agent.agent_id,
                'session_id': session_id,
                'activation_time': datetime.utcnow().isoformat(),
                'context_memories_used': len(context_used.get('memories', [])),
                'agent_type': agent.agent_type,
                'specializations': agent.specializations
            }
        )
        
        return memory_result.get('success', False)
    
    def store_agent_session_summary(self, agent: BMadAgent, session_summary: Dict[str, Any]) -> bool:
        """Store comprehensive agent session summary."""
        
        memory_content = f"""AGENT_SESSION: {agent.name} ({agent.agent_id}) session completed
Duration: {session_summary.get('duration', 'unknown')}
Tasks Completed: {session_summary.get('tasks_completed', 0)}
Quality Score: {session_summary.get('average_quality', 'N/A')}
Key Achievements: {'; '.join(session_summary.get('achievements', []))}
Lessons Learned: {'; '.join(session_summary.get('lessons', []))}
Handoff Notes: {session_summary.get('handoff_notes', 'None')}"""
        
        return self._store_memory(
            session_summary.get('user_id'), memory_content, 'AGENT_SESSIONS',
            {
                'agent_id': agent.agent_id,
                'session_id': session_summary.get('session_id'),
                'performance_metrics': session_summary.get('metrics', {}),
                'collaboration_quality': session_summary.get('collaboration_score')
            }
        ).get('success', False)
    
    # =============================================
    # WORKFLOW MEMORY INTEGRATION
    # =============================================
    
    def get_workflow_context(self, workflow_type: str, user_id: str, 
                           project_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get memory context for workflow initiation."""
        
        # Build workflow-specific searches
        search_queries = [
            f"WORKFLOW_PATTERNS {workflow_type} successful completion optimization",
            f"WORKFLOW_OPTIMIZATION {workflow_type} performance bottleneck",
            f"USER_PREFERENCES {user_id} workflow {workflow_type} configuration"
        ]
        
        # Add project-specific context
        if project_context:
            project_type = project_context.get('project_type', '')
            tech_stack = project_context.get('tech_stack', [])
            if project_type:
                search_queries.append(f"WORKFLOW_PATTERNS {workflow_type} {project_type}")
            if tech_stack:
                tech_context = ' '.join(tech_stack[:3])  # Limit to top 3 technologies
                search_queries.append(f"WORKFLOW_PATTERNS {workflow_type} {tech_context}")
        
        # Execute searches and aggregate results
        workflow_memories = self._aggregate_memory_searches(search_queries, user_id)
        
        # Extract workflow insights
        insights = self._extract_workflow_insights(workflow_memories, workflow_type)
        
        return {
            'memories': workflow_memories,
            'insights': insights,
            'recommended_agents': insights.get('recommended_agents', []),
            'optimization_tips': insights.get('optimization_tips', []),
            'potential_issues': insights.get('potential_issues', []),
            'estimated_duration': insights.get('estimated_duration'),
            'success_probability': insights.get('success_probability', 0.8)
        }
    
    def store_workflow_completion_memory(self, workflow: BMadWorkflow, 
                                       completion_data: Dict[str, Any]) -> bool:
        """Store comprehensive workflow completion memory."""
        
        memory_content = f"""WORKFLOW_COMPLETION: {workflow.workflow_type.value} - {workflow.name}
Duration: {completion_data.get('actual_duration', 'N/A')} hours
Success Rate: {completion_data.get('success_rate', 'N/A')}%
Agent Utilization: {completion_data.get('agent_utilization', {})}
Key Optimizations: {'; '.join(completion_data.get('optimizations', []))}
Bottlenecks Identified: {'; '.join(completion_data.get('bottlenecks', []))}
Quality Metrics: {completion_data.get('quality_summary', 'N/A')}
Lessons Learned: {'; '.join(completion_data.get('lessons', []))}"""
        
        return self._store_memory(
            workflow.user_id, memory_content, 'WORKFLOW_PATTERNS',
            {
                'workflow_id': workflow.workflow_id,
                'workflow_type': workflow.workflow_type.value,
                'completion_metrics': completion_data.get('metrics', {}),
                'performance_data': completion_data.get('performance', {})
            }
        ).get('success', False)
    
    # =============================================
    # TASK MEMORY INTEGRATION
    # =============================================
    
    def get_task_context(self, task_type: str, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Get memory context for task execution."""
        
        search_queries = [
            f"TASK_COMPLETION {task_type} {agent_id} successful quality",
            f"AGENT_CONTEXT {agent_id} {task_type} optimization",
            f"QUALITY_METRICS {task_type} improvement standards"
        ]
        
        task_memories = self._aggregate_memory_searches(search_queries, user_id)
        task_insights = self._extract_task_insights(task_memories, task_type, agent_id)
        
        return {
            'memories': task_memories,
            'insights': task_insights,
            'best_practices': task_insights.get('best_practices', []),
            'common_pitfalls': task_insights.get('common_pitfalls', []),
            'quality_criteria': task_insights.get('quality_criteria', []),
            'estimated_duration': task_insights.get('estimated_duration'),
            'success_tips': task_insights.get('success_tips', [])
        }
    
    def store_task_completion_memory(self, task: BMadTask, completion_data: Dict[str, Any]) -> bool:
        """Store task completion with rich context."""
        
        memory_content = f"""TASK_COMPLETION: {task.name} ({task.task_type})
Agent: {task.assigned_agent.name if task.assigned_agent else 'Unknown'}
Duration: {task.actual_hours or 'N/A'} hours (estimated: {task.estimated_hours or 'N/A'})
Quality Score: {task.quality_score or 'N/A'}/100
Success Factors: {'; '.join(completion_data.get('success_factors', []))}
Challenges Faced: {'; '.join(completion_data.get('challenges', []))}
Output Quality: {completion_data.get('output_quality', 'N/A')}
Lessons Learned: {'; '.join(completion_data.get('lessons', []))}"""
        
        return self._store_memory(
            task.user_id, memory_content, 'TASK_COMPLETION',
            {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'agent_id': task.assigned_agent.agent_id if task.assigned_agent else None,
                'performance_metrics': completion_data.get('metrics', {}),
                'quality_data': completion_data.get('quality_data', {})
            }
        ).get('success', False)
    
    # =============================================
    # COLLABORATION MEMORY INTEGRATION
    # =============================================
    
    def store_collaboration_memory(self, primary_agent: BMadAgent, 
                                 collaborating_agent: BMadAgent,
                                 collaboration_data: Dict[str, Any]) -> bool:
        """Store agent collaboration patterns and effectiveness."""
        
        memory_content = f"""AGENT_COLLABORATION: {primary_agent.name} → {collaborating_agent.name}
Context: {collaboration_data.get('context', 'Unknown')}
Duration: {collaboration_data.get('duration', 'N/A')} hours
Success Rating: {collaboration_data.get('success_rating', 'N/A')}/100
Handoff Quality: {collaboration_data.get('handoff_quality', 'N/A')}/100
Communication Effectiveness: {collaboration_data.get('communication_score', 'N/A')}/100
Key Success Factors: {'; '.join(collaboration_data.get('success_factors', []))}
Areas for Improvement: {'; '.join(collaboration_data.get('improvement_areas', []))}"""
        
        return self._store_memory(
            collaboration_data.get('user_id'), memory_content, 'AGENT_COLLABORATION',
            {
                'primary_agent': primary_agent.agent_id,
                'collaborating_agent': collaborating_agent.agent_id,
                'collaboration_type': collaboration_data.get('type', 'unknown'),
                'effectiveness_metrics': collaboration_data.get('metrics', {})
            }
        ).get('success', False)
    
    # =============================================
    # ANALYTICS AND INSIGHTS
    # =============================================
    
    def get_memory_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive memory analytics for BMAD operations."""
        
        # Get recent BMAD memories
        bmad_memories = self._get_bmad_memories(user_id, days)
        
        # Analyze memory patterns
        patterns = self._analyze_memory_patterns(bmad_memories)
        
        # Calculate effectiveness metrics
        effectiveness = self._calculate_memory_effectiveness(bmad_memories)
        
        return {
            'total_bmad_memories': len(bmad_memories),
            'category_distribution': patterns.get('categories', {}),
            'memory_effectiveness': effectiveness,
            'top_agents': patterns.get('top_agents', []),
            'successful_workflows': patterns.get('successful_workflows', []),
            'optimization_opportunities': patterns.get('optimizations', []),
            'memory_quality_score': effectiveness.get('quality_score', 0),
            'usage_trends': patterns.get('trends', {})
        }
    
    # =============================================
    # PRIVATE HELPER METHODS
    # =============================================
    
    def _search_memories(self, query: str, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Execute memory search with error handling."""
        try:
            response = requests.post(
                f"{self.memory_api_url}/memories/filter",
                json={
                    "user_id": user_id,
                    "search_query": query,
                    "page": 1,
                    "size": limit,
                    "sort_column": "created_at",
                    "sort_direction": "desc"
                },
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Memory search error: {e}")
        
        return {"items": [], "total": 0}
    
    def _store_memory(self, user_id: str, content: str, category: str, 
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store memory with error handling."""
        try:
            response = requests.post(
                f"{self.memory_api_url}/memories/",
                json={
                    "user_id": user_id,
                    "content": content,
                    "category": category,
                    "metadata": metadata or {}
                },
                headers=self.headers
            )
            
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Memory storage error: {e}")
        
        return {"success": False}
    
    def _get_related_memories(self, memories: List[Dict], user_id: str) -> List[Dict]:
        """Get related memories for provided memories."""
        enhanced_memories = memories.copy()
        
        for memory in memories[:3]:  # Get related for top 3 memories
            try:
                memory_id = memory.get('id')
                if memory_id:
                    response = requests.get(
                        f"{self.memory_api_url}/memories/{memory_id}/related",
                        params={"user_id": user_id}
                    )
                    
                    if response.status_code == 200:
                        related_data = response.json()
                        related_memories = related_data.get("items", [])
                        enhanced_memories.extend(related_memories[:2])  # Add top 2 related
            except Exception:
                continue
        
        return enhanced_memories
    
    def _calculate_context_scores(self, memories: List[Dict], entity_id: str) -> Dict[str, float]:
        """Calculate relevance scores for memory context."""
        scores = {
            'overall_relevance': 0.0,
            'recency_score': 0.0,
            'entity_specificity': 0.0,
            'category_diversity': 0.0
        }
        
        if not memories:
            return scores
        
        # Calculate overall relevance
        relevance_scores = [m.get('relevance_score', 0) for m in memories]
        scores['overall_relevance'] = sum(relevance_scores) / len(relevance_scores)
        
        # Calculate recency score
        now = datetime.utcnow()
        recency_scores = []
        for memory in memories:
            created_at = memory.get('created_at', 0)
            if isinstance(created_at, (int, float)):
                memory_date = datetime.fromtimestamp(created_at)
                days_old = (now - memory_date).days
                recency_score = max(0, 1 - (days_old / 30))  # Decay over 30 days
                recency_scores.append(recency_score)
        
        if recency_scores:
            scores['recency_score'] = sum(recency_scores) / len(recency_scores)
        
        # Calculate entity specificity
        entity_mentions = sum(1 for m in memories if entity_id.lower() in m.get('content', '').lower())
        scores['entity_specificity'] = entity_mentions / len(memories) if memories else 0
        
        # Calculate category diversity
        categories = set(m.get('category', 'GENERAL') for m in memories)
        scores['category_diversity'] = len(categories) / max(len(self.bmad_categories), 1)
        
        return scores
    
    def _aggregate_memory_searches(self, queries: List[str], user_id: str) -> List[Dict]:
        """Execute multiple searches and aggregate unique results."""
        all_memories = []
        seen_ids = set()
        
        for query in queries:
            memories = self._search_memories(query, user_id, limit=8)
            for memory in memories.get('items', []):
                memory_id = memory.get('id')
                if memory_id not in seen_ids:
                    seen_ids.add(memory_id)
                    all_memories.append(memory)
        
        # Sort by relevance and recency
        all_memories.sort(key=lambda m: (
            m.get('relevance_score', 0), 
            m.get('created_at', 0)
        ), reverse=True)
        
        return all_memories[:15]  # Return top 15 unique memories
    
    def _extract_activation_insights(self, memories: List[Dict], agent_id: str) -> Dict[str, Any]:
        """Extract actionable insights for agent activation."""
        insights = {
            'recommended_specializations': [],
            'optimal_contexts': [],
            'performance_tips': [],
            'collaboration_preferences': []
        }
        
        for memory in memories:
            content = memory.get('content', '').lower()
            
            # Extract specializations mentioned
            if 'specialization' in content or 'expert' in content:
                insights['recommended_specializations'].append(
                    self._extract_keywords(content, ['specialization', 'expert', 'skill'])
                )
            
            # Extract performance insights
            if 'performance' in content or 'optimization' in content:
                insights['performance_tips'].append(
                    self._extract_sentence_containing(content, ['performance', 'optimization', 'improve'])
                )
        
        # Clean up insights
        for key in insights:
            insights[key] = [item for item in insights[key] if item and len(item) > 10][:3]
        
        return insights
    
    def _extract_workflow_insights(self, memories: List[Dict], workflow_type: str) -> Dict[str, Any]:
        """Extract workflow-specific insights from memories."""
        insights = {
            'recommended_agents': [],
            'optimization_tips': [],
            'potential_issues': [],
            'estimated_duration': None,
            'success_probability': 0.8
        }
        
        duration_mentions = []
        success_indicators = 0
        total_workflows = 0
        
        for memory in memories:
            content = memory.get('content', '').lower()
            
            # Extract duration estimates
            if 'duration' in content or 'hours' in content:
                duration = self._extract_duration(content)
                if duration:
                    duration_mentions.append(duration)
            
            # Count success indicators
            if any(word in content for word in ['success', 'completed', 'achieved']):
                success_indicators += 1
            
            if workflow_type.lower() in content:
                total_workflows += 1
        
        # Calculate insights
        if duration_mentions:
            insights['estimated_duration'] = sum(duration_mentions) / len(duration_mentions)
        
        if total_workflows > 0:
            insights['success_probability'] = min(0.95, success_indicators / total_workflows)
        
        return insights
    
    def _extract_task_insights(self, memories: List[Dict], task_type: str, agent_id: str) -> Dict[str, Any]:
        """Extract task-specific insights from memories."""
        insights = {
            'best_practices': [],
            'common_pitfalls': [],
            'quality_criteria': [],
            'estimated_duration': None,
            'success_tips': []
        }
        
        # Analyze memories for task-specific patterns
        for memory in memories:
            content = memory.get('content', '').lower()
            
            if 'best practice' in content or 'recommendation' in content:
                insights['best_practices'].append(
                    self._extract_sentence_containing(content, ['practice', 'recommend'])
                )
            
            if 'avoid' in content or 'pitfall' in content or 'issue' in content:
                insights['common_pitfalls'].append(
                    self._extract_sentence_containing(content, ['avoid', 'pitfall', 'issue'])
                )
        
        # Clean up insights
        for key in ['best_practices', 'common_pitfalls', 'success_tips']:
            insights[key] = [item for item in insights[key] if item and len(item) > 15][:3]
        
        return insights
    
    def _format_agent_activation_memory(self, agent: BMadAgent, context_used: Dict[str, Any]) -> str:
        """Format agent activation memory with structured content."""
        return f"""AGENT_ACTIVATION: {agent.name} ({agent.agent_id}) activated successfully
Agent Type: {agent.agent_type}
Specializations: {', '.join(agent.specializations or [])}
Context Memories Used: {len(context_used.get('memories', []))}
Context Quality Score: {context_used.get('context_scores', {}).get('overall_relevance', 0):.2f}
Memory Categories: {', '.join(context_used.get('categories', []))}
Activation Timestamp: {datetime.utcnow().isoformat()}"""
    
    def _create_memory_integration_record(self, entity_type: str, entity_id: str,
                                        memory_category: str, context_type: str,
                                        memories: List[Dict], context_scores: Dict) -> Optional['BMadMemoryIntegration']:
        """Create a memory integration record in the database."""
        try:
            integration = BMadMemoryIntegration(
                bmad_entity_type=entity_type,
                bmad_entity_id=entity_id,
                memory_category=memory_category,
                context_type=context_type,
                relevance_score=context_scores.get('overall_relevance', 0),
                access_count=1,
                last_accessed=datetime.utcnow(),
                created_context={
                    'memory_count': len(memories),
                    'categories': list(set(m.get('category', 'GENERAL') for m in memories)),
                    'context_scores': context_scores
                }
            )
            
            self.db.add(integration)
            self.db.commit()
            return integration
        except Exception as e:
            print(f"Error creating memory integration record: {e}")
            return None
    
    def _extract_keywords(self, text: str, seed_words: List[str]) -> str:
        """Extract relevant keywords from text around seed words."""
        words = text.split()
        for i, word in enumerate(words):
            if any(seed in word for seed in seed_words):
                start = max(0, i - 3)
                end = min(len(words), i + 4)
                return ' '.join(words[start:end])
        return ''
    
    def _extract_sentence_containing(self, text: str, keywords: List[str]) -> str:
        """Extract sentence containing specified keywords."""
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence for keyword in keywords):
                return sentence.strip()
        return ''
    
    def _extract_duration(self, text: str) -> Optional[float]:
        """Extract duration in hours from text."""
        import re
        
        # Look for patterns like "2.5 hours", "3h", "120 minutes"
        hour_pattern = r'(\d+\.?\d*)\s*(?:hour|h)'
        minute_pattern = r'(\d+)\s*(?:minute|min)'
        
        hour_match = re.search(hour_pattern, text, re.IGNORECASE)
        if hour_match:
            return float(hour_match.group(1))
        
        minute_match = re.search(minute_pattern, text, re.IGNORECASE)
        if minute_match:
            return float(minute_match.group(1)) / 60
        
        return None
    
    def _get_bmad_memories(self, user_id: str, days: int) -> List[Dict]:
        """Get BMAD-related memories from the specified time period."""
        bmad_query = "AGENT_CONTEXT OR WORKFLOW_PATTERNS OR TASK_COMPLETION OR AGENT_COLLABORATION"
        return self._search_memories(bmad_query, user_id, limit=50).get('items', [])
    
    def _analyze_memory_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in BMAD memories."""
        patterns = {
            'categories': {},
            'top_agents': [],
            'successful_workflows': [],
            'optimizations': [],
            'trends': {}
        }
        
        # Analyze category distribution
        for memory in memories:
            category = memory.get('category', 'GENERAL')
            patterns['categories'][category] = patterns['categories'].get(category, 0) + 1
        
        return patterns
    
    def _calculate_memory_effectiveness(self, memories: List[Dict]) -> Dict[str, Any]:
        """Calculate effectiveness metrics for memory usage."""
        if not memories:
            return {'quality_score': 0, 'usage_frequency': 0, 'context_relevance': 0}
        
        # Calculate average quality indicators
        relevance_scores = [m.get('relevance_score', 0) for m in memories]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        return {
            'quality_score': min(100, avg_relevance * 100),
            'usage_frequency': len(memories),
            'context_relevance': avg_relevance,
            'memory_diversity': len(set(m.get('category', 'GENERAL') for m in memories))
        } 