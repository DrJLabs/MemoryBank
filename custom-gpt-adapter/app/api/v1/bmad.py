from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.api.deps import get_db
from app.services.bmad_service import BMadService
from app.models.bmad_models import (
    TaskStatus, TaskPriority, 
    WorkflowType
)
from pydantic import BaseModel

router = APIRouter()

# =============================================
# PYDANTIC MODELS FOR API
# =============================================

class AgentActivationRequest(BaseModel):
    agent_id: str
    user_id: str
    session_id: str
    memory_context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    id: str
    agent_id: str
    name: str
    title: Optional[str]
    agent_type: str
    status: str
    last_activity: Optional[datetime]
    total_tasks_completed: int
    success_rate: float
    efficiency_score: float
    current_workflow_id: Optional[str]
    memory_context: Dict[str, Any]

class WorkflowStartRequest(BaseModel):
    workflow_type: str
    user_id: str
    session_id: str
    project_types: Optional[List[str]] = None
    epic_id: Optional[str] = None

class WorkflowResponse(BaseModel):
    id: str
    workflow_id: str
    name: str
    workflow_type: str
    status: str
    progress_percentage: float
    start_time: Optional[datetime]
    estimated_duration: Optional[float]
    current_stage: Optional[str]
    user_id: str

class TaskCreateRequest(BaseModel):
    name: str
    task_type: str
    agent_id: str
    workflow_id: Optional[str] = None
    story_id: Optional[str] = None
    description: Optional[str] = None
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    dependencies: Optional[List[str]] = None
    template_used: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    task_id: str
    name: str
    description: Optional[str]
    task_type: str
    status: str
    priority: str
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    quality_score: Optional[float]
    assigned_agent_id: Optional[str]

class TaskCompletionRequest(BaseModel):
    output_data: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    execution_log: Optional[List[Dict]] = None

class StoryCreateRequest(BaseModel):
    story_id: str
    title: str
    epic_id: Optional[str] = None
    user_story: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    assigned_agent_id: Optional[str] = None
    workflow_id: Optional[str] = None

class EpicCreateRequest(BaseModel):
    epic_id: str
    name: str
    description: Optional[str] = None
    business_objective: Optional[str] = None
    stakeholders: Optional[List[str]] = None

class MemoryContextRequest(BaseModel):
    agent_id: str
    user_id: str
    query: Optional[str] = None

class MemoryStoreRequest(BaseModel):
    agent_id: str
    user_id: str
    content: str
    category: str = "AGENT_CONTEXT"

# =============================================
# AGENT MANAGEMENT ENDPOINTS
# =============================================

@router.post("/agents/activate", response_model=AgentResponse)
def activate_agent(
    request: AgentActivationRequest,
    db: Session = Depends(get_db)
):
    """Activate a BMAD agent with memory context integration"""
    try:
        service = BMadService(db)
        agent = service.activate_agent(
            request.agent_id, 
            request.user_id, 
            request.session_id,
            request.memory_context
        )
        
        return AgentResponse(
            id=str(agent.id),
            agent_id=agent.agent_id,
            name=agent.name,
            title=agent.title,
            agent_type=agent.agent_type,
            status=agent.status.value,
            last_activity=agent.last_activity,
            total_tasks_completed=agent.total_tasks_completed,
            success_rate=agent.success_rate,
            efficiency_score=agent.efficiency_score,
            current_workflow_id=str(agent.current_workflow_id) if agent.current_workflow_id else None,
            memory_context=agent.memory_context or {}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate agent: {str(e)}")

@router.get("/agents/active", response_model=List[AgentResponse])
def get_active_agents(
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all currently active agents"""
    service = BMadService(db)
    agents = service.get_active_agents(user_id)
    
    return [
        AgentResponse(
            id=str(agent.id),
            agent_id=agent.agent_id,
            name=agent.name,
            title=agent.title,
            agent_type=agent.agent_type,
            status=agent.status.value,
            last_activity=agent.last_activity,
            total_tasks_completed=agent.total_tasks_completed,
            success_rate=agent.success_rate,
            efficiency_score=agent.efficiency_score,
            current_workflow_id=str(agent.current_workflow_id) if agent.current_workflow_id else None,
            memory_context=agent.memory_context or {}
        )
        for agent in agents
    ]

@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent_details(
    agent_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific agent"""
    service = BMadService(db)
    agent = service.get_agent_by_id(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    return AgentResponse(
        id=str(agent.id),
        agent_id=agent.agent_id,
        name=agent.name,
        title=agent.title,
        agent_type=agent.agent_type,
        status=agent.status.value,
        last_activity=agent.last_activity,
        total_tasks_completed=agent.total_tasks_completed,
        success_rate=agent.success_rate,
        efficiency_score=agent.efficiency_score,
        current_workflow_id=str(agent.current_workflow_id) if agent.current_workflow_id else None,
        memory_context=agent.memory_context or {}
    )

@router.post("/agents/{agent_id}/deactivate")
def deactivate_agent(
    agent_id: str = Path(...),
    reason: str = Query("manual"),
    db: Session = Depends(get_db)
):
    """Deactivate an agent and cleanup resources"""
    try:
        service = BMadService(db)
        agent = service.deactivate_agent(agent_id, reason)
        return {"message": f"Agent {agent_id} deactivated successfully", "status": agent.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate agent: {str(e)}")

@router.get("/agents/{agent_id}/analytics")
def get_agent_analytics(
    agent_id: str = Path(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a specific agent"""
    service = BMadService(db)
    analytics = service.get_agent_analytics(agent_id, days)
    return analytics

# =============================================
# WORKFLOW MANAGEMENT ENDPOINTS
# =============================================

@router.post("/workflows/start", response_model=WorkflowResponse)
def start_workflow(
    request: WorkflowStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new BMAD workflow"""
    try:
        # Convert string to WorkflowType enum
        workflow_type = WorkflowType(request.workflow_type)
        
        service = BMadService(db)
        workflow = service.start_workflow(
            workflow_type,
            request.user_id,
            request.session_id,
            request.project_types,
            request.epic_id
        )
        
        return WorkflowResponse(
            id=str(workflow.id),
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            workflow_type=workflow.workflow_type.value,
            status=workflow.status.value,
            progress_percentage=workflow.progress_percentage,
            start_time=workflow.start_time,
            estimated_duration=workflow.estimated_duration,
            current_stage=workflow.current_stage,
            user_id=workflow.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@router.get("/workflows/active", response_model=List[WorkflowResponse])
def get_active_workflows(
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active workflows"""
    service = BMadService(db)
    workflows = service.get_active_workflows(user_id)
    
    return [
        WorkflowResponse(
            id=str(workflow.id),
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            workflow_type=workflow.workflow_type.value,
            status=workflow.status.value,
            progress_percentage=workflow.progress_percentage,
            start_time=workflow.start_time,
            estimated_duration=workflow.estimated_duration,
            current_stage=workflow.current_stage,
            user_id=workflow.user_id
        )
        for workflow in workflows
    ]

@router.post("/workflows/{workflow_id}/pause")
def pause_workflow(
    workflow_id: str = Path(...),
    reason: str = Query("manual"),
    db: Session = Depends(get_db)
):
    """Pause a workflow and update agent assignments"""
    try:
        service = BMadService(db)
        workflow = service.pause_workflow(workflow_id, reason)
        return {
            "message": f"Workflow {workflow_id} paused successfully",
            "status": workflow.status.value,
            "reason": reason
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/resume")
def resume_workflow(
    workflow_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """Resume a paused workflow"""
    try:
        service = BMadService(db)
        workflow = service.resume_workflow(workflow_id)
        return {
            "message": f"Workflow {workflow_id} resumed successfully",
            "status": workflow.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume workflow: {str(e)}")

@router.get("/workflows/analytics")
def get_workflow_analytics(
    workflow_type: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get workflow performance analytics"""
    service = BMadService(db)
    wf_type = WorkflowType(workflow_type) if workflow_type else None
    analytics = service.get_workflow_analytics(wf_type, days)
    return analytics

# =============================================
# TASK MANAGEMENT ENDPOINTS
# =============================================

@router.post("/tasks/create", response_model=TaskResponse)
def create_task(
    request: TaskCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new BMAD task"""
    try:
        priority = TaskPriority(request.priority)
        
        service = BMadService(db)
        task = service.create_task(
            name=request.name,
            task_type=request.task_type,
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            story_id=request.story_id,
            description=request.description,
            priority=priority,
            estimated_hours=request.estimated_hours,
            due_date=request.due_date,
            dependencies=request.dependencies,
            template_used=request.template_used,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        return TaskResponse(
            id=str(task.id),
            task_id=task.task_id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            status=task.status.value,
            priority=task.priority.value,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            start_time=task.start_time,
            end_time=task.end_time,
            quality_score=task.quality_score,
            assigned_agent_id=str(task.assigned_agent_id) if task.assigned_agent_id else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.post("/tasks/{task_id}/start")
def start_task(
    task_id: str = Path(...),
    agent_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Start a task and update agent status"""
    try:
        service = BMadService(db)
        task = service.start_task(task_id, agent_id)
        return {
            "message": f"Task {task_id} started successfully",
            "status": task.status.value,
            "start_time": task.start_time
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")

@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: str = Path(...),
    request: TaskCompletionRequest = None,
    db: Session = Depends(get_db)
):
    """Complete a task and update metrics"""
    try:
        service = BMadService(db)
        task = service.complete_task(
            task_id,
            request.output_data if request else None,
            request.quality_score if request else None,
            request.execution_log if request else None
        )
        return {
            "message": f"Task {task_id} completed successfully",
            "status": task.status.value,
            "actual_hours": task.actual_hours,
            "quality_score": task.quality_score
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")

@router.get("/agents/{agent_id}/tasks", response_model=List[TaskResponse])
def get_agent_tasks(
    agent_id: str = Path(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to an agent"""
    service = BMadService(db)
    task_status = TaskStatus(status) if status else None
    tasks = service.get_agent_tasks(agent_id, task_status)
    
    return [
        TaskResponse(
            id=str(task.id),
            task_id=task.task_id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            status=task.status.value,
            priority=task.priority.value,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            start_time=task.start_time,
            end_time=task.end_time,
            quality_score=task.quality_score,
            assigned_agent_id=str(task.assigned_agent_id) if task.assigned_agent_id else None
        )
        for task in tasks
    ]

# =============================================
# STORY AND EPIC MANAGEMENT ENDPOINTS
# =============================================

@router.post("/stories/create")
def create_story(
    request: StoryCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new story"""
    try:
        service = BMadService(db)
        story = service.create_story(
            request.story_id,
            request.title,
            request.epic_id,
            request.user_story,
            request.acceptance_criteria,
            request.assigned_agent_id,
            request.workflow_id
        )
        return {
            "id": str(story.id),
            "story_id": story.story_id,
            "title": story.title,
            "status": story.status.value,
            "message": f"Story {request.story_id} created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create story: {str(e)}")

@router.post("/epics/create")
def create_epic(
    request: EpicCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new epic"""
    try:
        service = BMadService(db)
        epic = service.create_epic(
            request.epic_id,
            request.name,
            request.description,
            request.business_objective,
            request.stakeholders
        )
        return {
            "id": str(epic.id),
            "epic_id": epic.epic_id,
            "name": epic.name,
            "status": epic.status.value,
            "message": f"Epic {request.epic_id} created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create epic: {str(e)}")

# =============================================
# MEMORY INTEGRATION ENDPOINTS
# =============================================

@router.post("/memory/context")
def get_memory_context(
    request: MemoryContextRequest,
    db: Session = Depends(get_db)
):
    """Get memory context for agent operations"""
    service = BMadService(db)
    context = service.get_agent_memory_context(
        request.agent_id,
        request.user_id,
        request.query
    )
    return context

@router.post("/memory/store")
def store_memory(
    request: MemoryStoreRequest,
    db: Session = Depends(get_db)
):
    """Store agent-related memory"""
    service = BMadService(db)
    result = service.store_agent_memory(
        request.agent_id,
        request.user_id,
        request.content,
        request.category
    )
    return result

# =============================================
# ANALYTICS AND REPORTING ENDPOINTS
# =============================================

@router.get("/analytics/overview")
def get_analytics_overview(
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get comprehensive BMAD system analytics"""
    service = BMadService(db)
    
    # Get agent analytics
    agent_analytics = service.get_agent_analytics(None, days)
    
    # Get workflow analytics
    workflow_analytics = service.get_workflow_analytics(None, days)
    
    # Get active agents and workflows
    active_agents = service.get_active_agents(user_id)
    active_workflows = service.get_active_workflows(user_id)
    
    return {
        "period_days": days,
        "user_id": user_id,
        "agents": {
            "active_count": len(active_agents),
            "analytics": agent_analytics
        },
        "workflows": {
            "active_count": len(active_workflows),
            "analytics": workflow_analytics
        },
        "summary": {
            "total_activities": agent_analytics.get("total_activities", 0),
            "total_workflows": workflow_analytics.get("total_workflows", 0),
            "overall_success_rate": agent_analytics.get("success_rate", 0),
            "workflow_completion_rate": workflow_analytics.get("completion_rate", 0)
        }
    }

@router.get("/health")
def health_check():
    """Health check endpoint for BMAD system"""
    return {
        "status": "healthy",
        "service": "BMAD API",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    } 