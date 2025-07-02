from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.bmad_service import BMadService
from app.models.bmad_models import (
    TaskStatus, TaskPriority
)

router = APIRouter(prefix="/bmad", tags=["BMAD System"])

# =============================================
# PYDANTIC MODELS
# =============================================

class AgentActivationRequest(BaseModel):
    agent_id: str
    session_id: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class AgentActivationResponse(BaseModel):
    agent_id: str
    name: str
    title: str
    status: str
    memory_context: Optional[Dict[str, Any]] = None
    message: str

class WorkflowStartRequest(BaseModel):
    workflow_id: str
    user_id: str
    session_id: str
    epic_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    status: str
    progress_percentage: float
    current_stage: Optional[str] = None
    start_time: datetime
    estimated_duration: Optional[float] = None

class TaskCreateRequest(BaseModel):
    name: str
    task_type: str
    agent_id: str
    workflow_id: Optional[str] = None
    story_id: Optional[str] = None
    description: Optional[str] = None
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    template_used: Optional[str] = None
    user_id: str
    session_id: str

class TaskResponse(BaseModel):
    task_id: str
    name: str
    status: str
    priority: str
    assigned_agent_id: str
    workflow_id: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    quality_score: Optional[float] = None

class MemoryContextRequest(BaseModel):
    agent_id: str
    query: str
    session_id: str
    user_id: str

class MemoryContextResponse(BaseModel):
    memories: List[Dict[str, Any]]
    total: int
    query: str
    confidence_score: Optional[float] = None

class AgentAnalyticsResponse(BaseModel):
    agent_count: int
    total_activities: int
    total_tasks: int
    completed_tasks: int
    active_tasks: int
    overall_success_rate: float
    agents: List[Dict[str, Any]]

class WorkflowAnalyticsResponse(BaseModel):
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    workflows: List[Dict[str, Any]]

# =============================================
# DEPENDENCY INJECTION
# =============================================

def get_bmad_service(db: Session = Depends(get_db)) -> BMadService:
    """Get BMadService instance"""
    return BMadService(db)

# =============================================
# AGENT ENDPOINTS
# =============================================

@router.post("/agents/activate", response_model=AgentActivationResponse)
async def activate_agent(
    request: AgentActivationRequest,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Activate a BMAD agent for a user session
    
    This endpoint:
    - Loads agent configuration from .bmad-core/agents/
    - Activates the agent with session context
    - Retrieves relevant memory context
    - Logs activation activity
    """
    try:
        agent = bmad_service.activate_agent(
            agent_id=request.agent_id,
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )
        
        return AgentActivationResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            title=agent.title or "",
            status=agent.status.value,
            memory_context=agent.context_data.get('memory_context'),
            message=f"Agent {agent.name} activated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate agent: {str(e)}"
        )

@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    session_id: str,
    user_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Deactivate a BMAD agent"""
    success = bmad_service.deactivate_agent(agent_id, session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not active"
        )
    
    return {"message": f"Agent {agent_id} deactivated successfully"}

@router.get("/agents/active")
async def get_active_agents(
    session_id: Optional[str] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Get all currently active agents"""
    agents = bmad_service.get_active_agents(session_id)
    
    return {
        "active_agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": agent.status.value,
                "session_id": agent.session_id,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
            }
            for agent in agents
        ],
        "count": len(agents)
    }

@router.get("/agents/{agent_id}")
async def get_agent_details(
    agent_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Get detailed information about an agent"""
    agent = bmad_service.get_agent_by_id(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}"
        )
    
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "title": agent.title,
        "agent_type": agent.agent_type.value,
        "status": agent.status.value,
        "capabilities": agent.capabilities,
        "specializations": agent.specializations,
        "tasks_completed": agent.tasks_completed,
        "success_rate": agent.success_rate,
        "average_completion_time": agent.average_completion_time,
        "workload_score": agent.workload_score,
        "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
    }

# =============================================
# WORKFLOW ENDPOINTS
# =============================================

@router.post("/workflows/start", response_model=WorkflowResponse)
async def start_workflow(
    request: WorkflowStartRequest,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Start a new BMAD workflow
    
    This endpoint:
    - Loads workflow configuration from .bmad-core/workflows/
    - Creates workflow instance with stages and tasks
    - Links to epic if provided
    - Stores workflow context in memory
    """
    try:
        workflow = bmad_service.start_workflow(
            workflow_id=request.workflow_id,
            user_id=request.user_id,
            session_id=request.session_id,
            epic_id=request.epic_id,
            context=request.context
        )
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            status=workflow.status.value,
            progress_percentage=workflow.progress_percentage,
            current_stage=workflow.current_stage,
            start_time=workflow.start_time,
            estimated_duration=workflow.estimated_duration
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.get("/workflows/active")
async def get_active_workflows(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Get all active workflows"""
    workflows = bmad_service.get_active_workflows(user_id, session_id)
    
    return {
        "active_workflows": [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "status": wf.status.value,
                "progress_percentage": wf.progress_percentage,
                "current_stage": wf.current_stage,
                "start_time": wf.start_time.isoformat() if wf.start_time else None
            }
            for wf in workflows
        ],
        "count": len(workflows)
    }

@router.get("/workflows/{workflow_id}")
async def get_workflow_details(
    workflow_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Get detailed workflow information"""
    workflow = bmad_service.get_workflow_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}"
        )
    
    return {
        "workflow_id": workflow.workflow_id,
        "name": workflow.name,
        "description": workflow.description,
        "workflow_type": workflow.workflow_type.value,
        "status": workflow.status.value,
        "progress_percentage": workflow.progress_percentage,
        "current_stage": workflow.current_stage,
        "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
        "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
        "estimated_duration": workflow.estimated_duration,
        "actual_duration": workflow.actual_duration,
        "project_types": workflow.project_types,
        "metadata": workflow.metadata
    }

@router.post("/workflows/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    agent_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Pause a workflow"""
    success = bmad_service.pause_workflow(workflow_id, agent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return {"message": f"Workflow {workflow_id} paused successfully"}

@router.post("/workflows/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    agent_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Resume a paused workflow"""
    success = bmad_service.resume_workflow(workflow_id, agent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return {"message": f"Workflow {workflow_id} resumed successfully"}

# =============================================
# TASK ENDPOINTS
# =============================================

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Create a new BMAD task"""
    try:
        # Convert priority string to enum
        priority = TaskPriority(request.priority.lower())
        
        task = bmad_service.create_task(
            name=request.name,
            task_type=request.task_type,
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            story_id=request.story_id,
            description=request.description,
            priority=priority,
            estimated_hours=request.estimated_hours,
            template_used=request.template_used,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        return TaskResponse(
            task_id=task.task_id,
            name=task.name,
            status=task.status.value,
            priority=task.priority.value,
            assigned_agent_id=task.assigned_agent.agent_id if task.assigned_agent else "",
            workflow_id=task.workflow.workflow_id if task.workflow else None,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            quality_score=task.quality_score
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.get("/agents/{agent_id}/tasks")
async def get_agent_tasks(
    agent_id: str,
    status_filter: Optional[str] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Get tasks assigned to an agent"""
    task_status = None
    if status_filter:
        try:
            task_status = TaskStatus(status_filter.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    tasks = bmad_service.get_agent_tasks(agent_id, task_status)
    
    return {
        "agent_id": agent_id,
        "tasks": [
            {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.value,
                "task_type": task.task_type,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ],
        "count": len(tasks)
    }

@router.post("/tasks/{task_id}/start")
async def start_task(
    task_id: str,
    agent_id: str,
    session_id: str,
    user_id: str,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Start executing a task"""
    success = bmad_service.start_task(task_id, agent_id, session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": f"Task {task_id} started successfully"}

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    agent_id: str,
    session_id: str,
    user_id: str,
    output_files: Optional[List[str]] = None,
    output_data: Optional[Dict[str, Any]] = None,
    quality_score: Optional[float] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Complete a task"""
    success = bmad_service.complete_task(
        task_id=task_id,
        agent_id=agent_id,
        session_id=session_id,
        user_id=user_id,
        output_files=output_files,
        output_data=output_data,
        quality_score=quality_score
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": f"Task {task_id} completed successfully"}

# =============================================
# MEMORY INTEGRATION ENDPOINTS
# =============================================

@router.post("/memory/context", response_model=MemoryContextResponse)
async def get_memory_context(
    request: MemoryContextRequest,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Get memory context for an agent
    
    This endpoint retrieves relevant memories from the memory service
    based on agent context and query, providing AI-enhanced context
    for agent operations.
    """
    try:
        context = bmad_service.get_agent_memory_context(
            agent_id=request.agent_id,
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        return MemoryContextResponse(
            memories=context["memories"],
            total=context["total"],
            query=context["query"],
            confidence_score=0.8  # Default confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve memory context: {str(e)}"
        )

@router.post("/memory/store")
async def store_agent_memory(
    agent_id: str,
    content: str,
    category: str,
    session_id: str,
    user_id: str,
    workflow_id: Optional[str] = None,
    task_id: Optional[str] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """Store new memory from agent activity"""
    success = bmad_service.store_agent_memory(
        agent_id=agent_id,
        content=content,
        category=category,
        session_id=session_id,
        user_id=user_id,
        workflow_id=workflow_id,
        task_id=task_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store memory"
        )
    
    return {"message": "Memory stored successfully"}

# =============================================
# ANALYTICS ENDPOINTS
# =============================================

@router.get("/analytics/agents", response_model=AgentAnalyticsResponse)
async def get_agent_analytics(
    agent_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Get comprehensive agent analytics
    
    Provides detailed metrics on agent performance, task completion,
    success rates, and activity patterns.
    """
    analytics = bmad_service.get_agent_analytics(agent_id, start_date, end_date)
    
    return AgentAnalyticsResponse(**analytics)

@router.get("/analytics/workflows", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    workflow_id: Optional[str] = None,
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Get workflow analytics
    
    Provides metrics on workflow execution, completion rates,
    duration analysis, and progress tracking.
    """
    analytics = bmad_service.get_workflow_analytics(workflow_id)
    
    return WorkflowAnalyticsResponse(**analytics)

@router.get("/analytics/system")
async def get_system_analytics(
    bmad_service: BMadService = Depends(get_bmad_service)
):
    """
    Get overall BMAD system analytics
    
    Provides high-level system metrics including:
    - Total agents, workflows, tasks, stories
    - System health and performance indicators
    - Usage patterns and trends
    """
    agent_analytics = bmad_service.get_agent_analytics()
    workflow_analytics = bmad_service.get_workflow_analytics()
    
    return {
        "system_overview": {
            "total_agents": agent_analytics["agent_count"],
            "active_agents": len([a for a in agent_analytics["agents"] if a["status"] == "active"]),
            "total_workflows": workflow_analytics["total_workflows"],
            "active_workflows": workflow_analytics["active_workflows"],
            "completed_workflows": workflow_analytics["completed_workflows"],
            "total_tasks": agent_analytics["total_tasks"],
            "completed_tasks": agent_analytics["completed_tasks"],
            "overall_success_rate": agent_analytics["overall_success_rate"]
        },
        "performance_metrics": {
            "average_task_completion_time": sum(
                a["average_completion_time"] for a in agent_analytics["agents"]
            ) / max(len(agent_analytics["agents"]), 1),
            "system_efficiency": agent_analytics["overall_success_rate"],
            "agent_utilization": len([a for a in agent_analytics["agents"] 
                                   if a["current_tasks"] > 0]) / max(len(agent_analytics["agents"]), 1) * 100
        }
    }

@router.get("/health")
async def bmad_health_check():
    """BMAD system health check"""
    return {
        "status": "healthy",
        "service": "BMAD System",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    } 