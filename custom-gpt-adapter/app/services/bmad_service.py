from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
import uuid
import requests

from app.models.bmad_models import (
    BMadAgent, BMadWorkflow, BMadTask, BMadStory, BMadEpic, 
    BMadWorkflowStage, BMadAgentActivity, AgentStatus, WorkflowStatus, TaskStatus,
    WorkflowType, TaskPriority
)
from app.core.config import settings

class BMadService:
    """
    Comprehensive BMAD system service providing:
    - Agent activation and management
    - Workflow orchestration
    - Task tracking and execution
    - Story and epic management
    - Memory integration
    - Analytics and reporting
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory_api_url = settings.MEMORY_BANK_API_URL
        self.memory_api_key = settings.MEMORY_BANK_API_KEY
    
    # =============================================
    # AGENT MANAGEMENT
    # =============================================
    
    def activate_agent(self, agent_id: str, user_id: str, session_id: str,
                      memory_context: Dict[str, Any] = None) -> BMadAgent:
        """Activate a BMAD agent with memory context integration"""
        
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Get memory context for agent activation
        if memory_context is None:
            memory_context = self._get_agent_memory_context(agent_id, user_id)
        
        # Update agent status and context
        agent.status = AgentStatus.ACTIVE
        agent.last_activity = datetime.utcnow()
        agent.current_session_id = session_id
        agent.current_user_id = user_id
        agent.memory_context = memory_context
        
        # Log activation activity
        self._log_agent_activity(
            agent.id, "agent_activated", session_id, user_id,
            {"memory_context_loaded": len(memory_context.get("memories", []))}
        )
        
        self.db.commit()
        return agent
    
    def get_agent_by_id(self, agent_id: str) -> Optional[BMadAgent]:
        """Get agent by agent ID"""
        return self.db.query(BMadAgent).filter(BMadAgent.agent_id == agent_id).first()
    
    def get_active_agents(self, user_id: str = None) -> List[BMadAgent]:
        """Get all currently active agents"""
        query = self.db.query(BMadAgent).filter(
            BMadAgent.status.in_([AgentStatus.ACTIVE, AgentStatus.BUSY])
        )
        if user_id:
            query = query.filter(BMadAgent.current_user_id == user_id)
        return query.all()
    
    def deactivate_agent(self, agent_id: str, reason: str = "manual") -> BMadAgent:
        """Deactivate an agent and cleanup resources"""
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Store final memories if agent was active
        if agent.status in [AgentStatus.ACTIVE, AgentStatus.BUSY]:
            self._store_agent_session_memories(agent)
        
        # Update agent status
        agent.status = AgentStatus.IDLE
        agent.current_session_id = None
        agent.current_user_id = None
        agent.memory_context = {}
        
        # Log deactivation
        self._log_agent_activity(
            agent.id, "agent_deactivated", agent.current_session_id, 
            agent.current_user_id, {"reason": reason}
        )
        
        self.db.commit()
        return agent
    
    def update_agent_metrics(self, agent_id: str, task_duration: float, 
                           success: bool) -> None:
        """Update agent performance metrics"""
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            return
        
        # Update completion count
        if success:
            agent.total_tasks_completed += 1
        
        # Update success rate
        total_activities = self.db.query(BMadAgentActivity).filter(
            BMadAgentActivity.agent_id == agent.id
        ).count()
        
        successful_activities = self.db.query(BMadAgentActivity).filter(
            and_(BMadAgentActivity.agent_id == agent.id, 
                 BMadAgentActivity.success)
        ).count()
        
        agent.success_rate = (successful_activities / max(total_activities, 1)) * 100
        
        # Update average task duration
        if agent.total_tasks_completed > 0:
            current_avg = agent.average_task_duration or 0
            agent.average_task_duration = (
                (current_avg * (agent.total_tasks_completed - 1) + task_duration) 
                / agent.total_tasks_completed
            )
        
        # Calculate efficiency score (combination of success rate and speed)
        base_efficiency = agent.success_rate * 0.7  # 70% weight on success
        speed_factor = min(100, max(0, 100 - (agent.average_task_duration * 10)))  # Speed component
        agent.efficiency_score = base_efficiency + (speed_factor * 0.3)  # 30% weight on speed
        
        self.db.commit()
    
    # =============================================
    # WORKFLOW MANAGEMENT
    # =============================================
    
    def start_workflow(self, workflow_type: WorkflowType, user_id: str, 
                      session_id: str, project_types: List[str] = None,
                      epic_id: str = None) -> BMadWorkflow:
        """Start a new BMAD workflow with proper initialization"""
        
        # Load workflow configuration from .bmad-core
        workflow_config = self._load_workflow_config(workflow_type.value)
        
        # Create workflow instance
        workflow = BMadWorkflow(
            workflow_id=f"{workflow_type.value}-{uuid.uuid4().hex[:8]}",
            name=workflow_config.get("name", workflow_type.value.replace("-", " ").title()),
            description=workflow_config.get("description", ""),
            workflow_type=workflow_type,
            status=WorkflowStatus.ACTIVE,
            project_types=project_types or [],
            sequence=workflow_config.get("sequence", []),
            user_id=user_id,
            session_id=session_id,
            parent_epic_id=epic_id,
            start_time=datetime.utcnow()
        )
        
        self.db.add(workflow)
        self.db.flush()  # Get the ID
        
        # Create workflow stages from sequence
        self._create_workflow_stages(workflow, workflow_config.get("sequence", []))
        
        # Create initial tasks
        self._create_workflow_tasks(workflow, workflow_config.get("sequence", []))
        
        # Store workflow pattern in memory
        self._store_workflow_memory(workflow, user_id)
        
        self.db.commit()
        return workflow
    
    def get_active_workflows(self, user_id: str = None) -> List[BMadWorkflow]:
        """Get all active workflows"""
        query = self.db.query(BMadWorkflow).filter(
            BMadWorkflow.status == WorkflowStatus.ACTIVE
        )
        if user_id:
            query = query.filter(BMadWorkflow.user_id == user_id)
        return query.order_by(desc(BMadWorkflow.start_time)).all()
    
    def pause_workflow(self, workflow_id: str, reason: str = "manual") -> BMadWorkflow:
        """Pause a workflow and update agent assignments"""
        workflow = self.db.query(BMadWorkflow).filter(
            BMadWorkflow.workflow_id == workflow_id
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow.status = WorkflowStatus.PAUSED
        
        # Update agents working on this workflow
        agents = self.db.query(BMadAgent).filter(
            BMadAgent.current_workflow_id == workflow.id
        ).all()
        
        for agent in agents:
            agent.status = AgentStatus.PAUSED
            self._log_agent_activity(
                agent.id, "workflow_paused", workflow.session_id, 
                workflow.user_id, {"workflow_id": workflow_id, "reason": reason}
            )
        
        self.db.commit()
        return workflow
    
    def resume_workflow(self, workflow_id: str) -> BMadWorkflow:
        """Resume a paused workflow"""
        workflow = self.db.query(BMadWorkflow).filter(
            BMadWorkflow.workflow_id == workflow_id
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow.status = WorkflowStatus.ACTIVE
        
        # Reactivate agents
        agents = self.db.query(BMadAgent).filter(
            BMadAgent.current_workflow_id == workflow.id
        ).all()
        
        for agent in agents:
            if agent.status == AgentStatus.PAUSED:
                agent.status = AgentStatus.ACTIVE
                self._log_agent_activity(
                    agent.id, "workflow_resumed", workflow.session_id,
                    workflow.user_id, {"workflow_id": workflow_id}
                )
        
        self.db.commit()
        return workflow
    
    # =============================================
    # TASK MANAGEMENT
    # =============================================
    
    def create_task(self, name: str, task_type: str, agent_id: str, 
                   workflow_id: str = None, story_id: str = None,
                   description: str = None, priority: TaskPriority = TaskPriority.MEDIUM,
                   estimated_hours: float = None, due_date: datetime = None,
                   dependencies: List[str] = None, template_used: str = None,
                   user_id: str = None, session_id: str = None) -> BMadTask:
        """Create a new BMAD task"""
        
        # Get agent
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Generate task ID
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        task = BMadTask(
            task_id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            priority=priority,
            assigned_agent_id=agent.id,
            workflow_id=workflow_id,
            story_id=story_id,
            estimated_hours=estimated_hours,
            due_date=due_date,
            dependencies=dependencies or [],
            template_used=template_used,
            user_id=user_id,
            session_id=session_id
        )
        
        self.db.add(task)
        self.db.commit()
        
        # Log task creation
        self._log_agent_activity(
            agent.id, "task_created", session_id, user_id,
            {"task_id": task.task_id, "task_type": task_type}
        )
        
        return task
    
    def start_task(self, task_id: str, agent_id: str = None) -> BMadTask:
        """Start a task and update agent status"""
        task = self.db.query(BMadTask).filter(BMadTask.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = datetime.utcnow()
        
        # Update agent status
        if task.assigned_agent_id:
            agent = self.db.query(BMadAgent).filter(
                BMadAgent.id == task.assigned_agent_id
            ).first()
            if agent:
                agent.status = AgentStatus.BUSY
                agent.last_activity = datetime.utcnow()
        
        # Log task start
        self._log_agent_activity(
            task.assigned_agent_id, "task_started", task.session_id, 
            task.user_id, {"task_id": task_id}
        )
        
        self.db.commit()
        return task
    
    def complete_task(self, task_id: str, output_data: Dict[str, Any] = None,
                     quality_score: float = None, execution_log: List[Dict] = None) -> BMadTask:
        """Complete a task and update metrics"""
        task = self.db.query(BMadTask).filter(BMadTask.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # Update task
        task.status = TaskStatus.COMPLETED
        task.end_time = datetime.utcnow()
        task.output_data = output_data or {}
        task.quality_score = quality_score
        task.execution_log = execution_log or []
        
        # Calculate actual hours
        if task.start_time:
            duration = task.end_time - task.start_time
            task.actual_hours = duration.total_seconds() / 3600
        
        # Update agent metrics
        if task.assigned_agent_id:
            agent = self.db.query(BMadAgent).filter(
                BMadAgent.id == task.assigned_agent_id
            ).first()
            if agent:
                agent.status = AgentStatus.ACTIVE  # Return to active
                self.update_agent_metrics(agent.agent_id, task.actual_hours, True)
        
        # Store task completion memory
        self._store_task_completion_memory(task)
        
        # Log task completion
        self._log_agent_activity(
            task.assigned_agent_id, "task_completed", task.session_id,
            task.user_id, {
                "task_id": task_id, 
                "duration_hours": task.actual_hours,
                "quality_score": quality_score
            }
        )
        
        self.db.commit()
        return task
    
    def get_agent_tasks(self, agent_id: str, status: TaskStatus = None) -> List[BMadTask]:
        """Get tasks assigned to an agent"""
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            return []
        
        query = self.db.query(BMadTask).filter(
            BMadTask.assigned_agent_id == agent.id
        )
        
        if status:
            query = query.filter(BMadTask.status == status)
        
        return query.order_by(desc(BMadTask.created_at)).all()
    
    # =============================================
    # STORY AND EPIC MANAGEMENT
    # =============================================
    
    def create_story(self, story_id: str, title: str, epic_id: str = None,
                    user_story: str = None, acceptance_criteria: List[str] = None,
                    assigned_agent_id: str = None, workflow_id: str = None) -> BMadStory:
        """Create a new story"""
        
        story = BMadStory(
            story_id=story_id,
            title=title,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria or [],
            epic_id=epic_id,
            assigned_agent_id=assigned_agent_id,
            workflow_id=workflow_id
        )
        
        self.db.add(story)
        self.db.commit()
        return story
    
    def create_epic(self, epic_id: str, name: str, description: str = None,
                   business_objective: str = None, stakeholders: List[str] = None) -> BMadEpic:
        """Create a new epic"""
        
        epic = BMadEpic(
            epic_id=epic_id,
            name=name,
            description=description,
            business_objective=business_objective,
            stakeholders=stakeholders or []
        )
        
        self.db.add(epic)
        self.db.commit()
        return epic
    
    # =============================================
    # MEMORY INTEGRATION
    # =============================================
    
    def get_agent_memory_context(self, agent_id: str, user_id: str, 
                                query: str = None) -> Dict[str, Any]:
        """Get memory context for agent operations"""
        try:
            # Use advanced memory integration
            context_query = query or f"agent {agent_id} context preferences workflow"
            
            # Call memory API for context
            response = requests.post(
                f"{self.memory_api_url}/memories/filter",
                json={
                    "user_id": user_id,
                    "search_query": context_query,
                    "page": 1,
                    "size": 10,
                    "sort_column": "created_at",
                    "sort_direction": "desc"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "memories": data.get("items", []),
                    "total": data.get("total", 0),
                    "query": context_query,
                    "categories": self._extract_memory_categories(data.get("items", []))
                }
        except Exception as e:
            print(f"Memory API error: {e}")
        
        return {"memories": [], "total": 0}
    
    def store_agent_memory(self, agent_id: str, user_id: str, content: str,
                          category: str = "AGENT_CONTEXT") -> Dict[str, Any]:
        """Store agent-related memory"""
        try:
            response = requests.post(
                f"{self.memory_api_url}/memories/",
                json={
                    "user_id": user_id,
                    "content": f"[{category}] AGENT_{agent_id.upper()}: {content}",
                    "category": category
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            print(f"Memory storage error: {e}")
        
        return {}
    
    # =============================================
    # ANALYTICS AND REPORTING
    # =============================================
    
    def get_agent_analytics(self, agent_id: str = None, 
                           days: int = 30) -> Dict[str, Any]:
        """Get comprehensive agent analytics"""
        
        # Base query
        start_date = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(BMadAgentActivity).filter(
            BMadAgentActivity.timestamp >= start_date
        )
        
        if agent_id:
            agent = self.get_agent_by_id(agent_id)
            if agent:
                query = query.filter(BMadAgentActivity.agent_id == agent.id)
        
        activities = query.all()
        
        # Calculate metrics
        total_activities = len(activities)
        successful_activities = len([a for a in activities if a.success])
        avg_response_time = sum([a.response_time or 0 for a in activities]) / max(total_activities, 1)
        
        # Activity breakdown
        activity_types = {}
        for activity in activities:
            activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
        
        return {
            "total_activities": total_activities,
            "success_rate": (successful_activities / max(total_activities, 1)) * 100,
            "average_response_time": avg_response_time,
            "activity_breakdown": activity_types,
            "period_days": days
        }
    
    def get_workflow_analytics(self, workflow_type: WorkflowType = None,
                              days: int = 30) -> Dict[str, Any]:
        """Get workflow performance analytics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(BMadWorkflow).filter(
            BMadWorkflow.created_at >= start_date
        )
        
        if workflow_type:
            query = query.filter(BMadWorkflow.workflow_type == workflow_type)
        
        workflows = query.all()
        
        # Calculate metrics
        total_workflows = len(workflows)
        completed_workflows = len([w for w in workflows if w.status == WorkflowStatus.COMPLETED])
        active_workflows = len([w for w in workflows if w.status == WorkflowStatus.ACTIVE])
        
        # Average duration for completed workflows
        completed = [w for w in workflows if w.status == WorkflowStatus.COMPLETED and w.actual_duration]
        avg_duration = sum([w.actual_duration for w in completed]) / max(len(completed), 1)
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "active_workflows": active_workflows,
            "completion_rate": (completed_workflows / max(total_workflows, 1)) * 100,
            "average_duration_hours": avg_duration,
            "period_days": days
        }
    
    # =============================================
    # PRIVATE HELPER METHODS
    # =============================================
    
    def _get_agent_memory_context(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive memory context for agent"""
        return self.get_agent_memory_context(agent_id, user_id)
    
    def _log_agent_activity(self, agent_id: str, activity_type: str, 
                           session_id: str, user_id: str, 
                           activity_data: Dict[str, Any] = None) -> BMadAgentActivity:
        """Log agent activity"""
        activity = BMadAgentActivity(
            agent_id=agent_id,
            activity_type=activity_type,
            activity_data=activity_data or {},
            session_id=session_id,
            user_id=user_id,
            success=True,  # Assume success unless specified
            timestamp=datetime.utcnow()
        )
        
        self.db.add(activity)
        return activity
    
    def _load_workflow_config(self, workflow_type: str) -> Dict[str, Any]:
        """Load workflow configuration from .bmad-core files"""
        # This would read from .bmad-core/workflows/{workflow_type}.yml
        # For now, return a basic configuration
        return {
            "name": workflow_type.replace("-", " ").title(),
            "description": f"BMAD {workflow_type} workflow",
            "sequence": [
                {"action": "planning", "agent": "pm"},
                {"action": "development", "agent": "dev"},
                {"action": "validation", "agent": "qa"}
            ]
        }
    
    def _create_workflow_stages(self, workflow: BMadWorkflow, sequence: List[Dict]) -> None:
        """Create workflow stages from sequence"""
        for idx, step in enumerate(sequence):
            if isinstance(step, dict):
                stage = BMadWorkflowStage(
                    workflow_id=workflow.id,
                    stage_id=f"stage-{idx+1}",
                    name=step.get('action', f"Stage {idx+1}"),
                    description=step.get('notes', ''),
                    sequence_order=idx,
                    assigned_agents=[step.get('agent', 'pm')]
                )
                self.db.add(stage)
    
    def _create_workflow_tasks(self, workflow: BMadWorkflow, sequence: List[Dict]) -> None:
        """Create initial tasks from workflow sequence"""
        for idx, step in enumerate(sequence):
            if isinstance(step, dict):
                task_name = step.get('creates', step.get('action', f"Task {idx+1}"))
                step.get('agent', 'pm')
                
                task = BMadTask(
                    task_id=f"{workflow.workflow_id}-task-{idx+1}",
                    name=task_name,
                    description=step.get('notes', step.get('action')),
                    task_type='workflow_step',
                    status=TaskStatus.PENDING,
                    assigned_agent_id=None,  # Assign when agent is available
                    workflow_id=workflow.id,
                    estimated_hours=2.0  # Default estimate
                )
                
                self.db.add(task)
    
    def _update_workflow_progress(self, workflow: BMadWorkflow) -> None:
        """Update workflow progress based on completed stages"""
        stages = self.db.query(BMadWorkflowStage).filter(
            BMadWorkflowStage.workflow_id == workflow.id
        ).all()
        
        if not stages:
            return
        
        completed_stages = len([s for s in stages if s.status == TaskStatus.COMPLETED])
        workflow.progress_percentage = (completed_stages / len(stages)) * 100
        
        if workflow.progress_percentage >= 100:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.end_time = datetime.utcnow()
            if workflow.start_time:
                duration = workflow.end_time - workflow.start_time
                workflow.actual_duration = duration.total_seconds() / 3600
    
    def _store_workflow_memory(self, workflow: BMadWorkflow, user_id: str) -> None:
        """Store workflow pattern in memory"""
        content = f"WORKFLOW_PATTERN: Started {workflow.workflow_type.value} workflow {workflow.workflow_id} - {workflow.name}"
        self.store_agent_memory("system", user_id, content, "WORKFLOW_PATTERNS")
    
    def _store_task_completion_memory(self, task: BMadTask) -> None:
        """Store task completion in memory"""
        if task.user_id:
            content = f"TASK_COMPLETION: {task.name} ({task.task_type}) completed in {task.actual_hours:.1f}h with quality {task.quality_score or 'N/A'}"
            self.store_agent_memory("system", task.user_id, content, "TASK_COMPLETION")
    
    def _store_agent_session_memories(self, agent: BMadAgent) -> None:
        """Store agent session memories before deactivation"""
        if agent.current_user_id and agent.memory_context:
            content = f"AGENT_SESSION: {agent.name} ({agent.agent_id}) session completed - {len(agent.memory_context.get('memories', []))} context items used"
            self.store_agent_memory(agent.agent_id, agent.current_user_id, content, "AGENT_SESSIONS")
    
    def _extract_memory_categories(self, memories: List[Dict]) -> List[str]:
        """Extract unique categories from memory list"""
        categories = set()
        for memory in memories:
            content = memory.get("content", "")
            # Extract category from content like [CATEGORY] or CATEGORY:
            if content.startswith("["):
                category = content.split("]")[0][1:]
                categories.add(category)
            elif ":" in content:
                potential_category = content.split(":")[0]
                if len(potential_category) < 20:  # Reasonable category length
                    categories.add(potential_category)
        
        return list(categories) 