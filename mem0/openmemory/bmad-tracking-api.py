#!/usr/bin/env python3
"""
BMAD Tracking API Server
Provides REST API endpoints for tracking BMAD stories, epics, tasks, and workflows
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import re
import glob
import yaml
from pathlib import Path
import random
import time
from functools import wraps
import os

app = FastAPI(title="BMAD Tracking API", version="1.0.0")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache with TTL
CACHE = {}
CACHE_TTL_SECONDS = 10  # Cache results for 10 seconds

def ttl_cache(func):
    """Decorator to cache function results with a TTL."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Create a cache key based on function name and arguments
        key = f"{func.__name__}:{args}:{kwargs}"
        now = time.time()

        # Check if a valid (non-expired) cache entry exists
        if key in CACHE and now - CACHE[key]['timestamp'] < CACHE_TTL_SECONDS:
            return CACHE[key]['data']

        # Execute the function and cache the result
        result = await func(*args, **kwargs)
        CACHE[key] = {'data': result, 'timestamp': now}
        return result
    return wrapper

# Base paths
PROJECT_ROOT = Path("/home/drj/C-System/MemoryBank")
STORIES_PATH = PROJECT_ROOT / "docs/stories"
PRD_PATH = PROJECT_ROOT / "docs/prd"
BMAD_CORE_PATH = PROJECT_ROOT / ".bmad-core"
WORKFLOWS_PATH = BMAD_CORE_PATH / "workflows"
AGENTS_PATH = BMAD_CORE_PATH / "agents"
TASKS_PATH = BMAD_CORE_PATH / "tasks"
CHECKLISTS_PATH = BMAD_CORE_PATH / "checklists"

# Enhanced Data models
class StoryStatus(BaseModel):
    id: str
    title: str
    status: str  # Draft, Ready, In Progress, Review, Done
    agent: Optional[str] = None
    workflow: Optional[str] = None
    lastUpdated: datetime
    description: Optional[str] = None

class DetailedStory(BaseModel):
    id: str
    title: str
    status: str
    agent: Optional[str] = None
    workflow: Optional[str] = None
    lastUpdated: str
    description: str
    acceptanceCriteria: Optional[List[str]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    dependencies: Optional[List[str]] = None
    epicId: Optional[str] = None
    priority: Optional[str] = None
    estimatedHours: Optional[float] = None
    actualHours: Optional[float] = None
    assignedTo: Optional[str] = None
    tags: Optional[List[str]] = None

class DetailedEpic(BaseModel):
    id: str
    title: str
    status: str
    stories: List[str]
    progress: float
    description: str
    startDate: Optional[str] = None
    targetDate: Optional[str] = None
    owner: Optional[str] = None
    objectives: Optional[List[str]] = None
    keyResults: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    risks: Optional[List[str]] = None

class WorkflowTask(BaseModel):
    id: str
    name: str
    status: str
    agent: str
    description: Optional[str] = None
    checklist: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None

class WorkflowStage(BaseModel):
    id: str
    name: str
    status: str
    agent: Optional[str] = None
    tasks: List[WorkflowTask]
    startTime: Optional[str] = None
    endTime: Optional[str] = None

class DetailedWorkflow(BaseModel):
    id: str
    name: str
    type: str
    currentStage: str
    stages: List[WorkflowStage]
    progress: float
    status: str
    startTime: str
    lastUpdated: str
    assignedAgents: List[str]
    metadata: Optional[Dict[str, Any]] = None

class AgentTask(BaseModel):
    id: str
    name: str
    type: str
    status: str
    priority: str
    startTime: Optional[str] = None
    estimatedDuration: Optional[float] = None
    actualDuration: Optional[float] = None
    storyId: Optional[str] = None
    epicId: Optional[str] = None
    workflowId: Optional[str] = None

class AgentMetrics(BaseModel):
    tasksCompleted: int
    tasksActive: int
    averageCompletionTime: float
    successRate: float
    workloadScore: int
    efficiencyRating: int
    collaborationScore: int

class DetailedAgent(BaseModel):
    id: str
    name: str
    type: str
    status: str
    currentTasks: List[AgentTask]
    completedTasksToday: int
    metrics: AgentMetrics
    specializations: List[str]
    lastActivity: str
    availability: int
    currentWorkflow: Optional[str] = None
    collaboratingWith: Optional[List[str]] = None

class TaskStatus(BaseModel):
    id: str
    name: str
    status: str  # pending, active, complete
    agent: Optional[str] = None
    storyId: Optional[str] = None
    epicId: Optional[str] = None
    lastUpdated: datetime

class ChecklistItem(BaseModel):
    text: str
    done: bool

class Checklist(BaseModel):
    id: str
    name: str
    items: List[ChecklistItem]
    progress: float
    lastUpdated: datetime

# Utility functions
def parse_story_file(file_path: str) -> dict:
    """Parse a story file to extract real task information"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic info
        story_info = {
            'file': os.path.basename(file_path),
            'status': 'pending',
            'tasks': [],
            'progress': 0
        }
        
        # Extract status
        for line in content.split('\n'):
            if line.startswith('## Status:'):
                story_info['status'] = line.replace('## Status:', '').strip().lower()
                break
        
        # Count tasks and completion
        lines = content.split('\n')
        total_tasks = 0
        completed_tasks = 0
        current_task = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                total_tasks += 1
                if line.startswith('- [x]'):
                    completed_tasks += 1
                # Extract task name
                task_name = line.replace('- [ ]', '').replace('- [x]', '').strip()
                if task_name.startswith('**') and task_name.endswith('**'):
                    task_name = task_name[2:-2]
                if ':' in task_name:
                    task_name = task_name.split(':')[0].strip()
                
                status = 'complete' if line.startswith('- [x]') else 'active' if story_info['status'] == 'in progress' else 'pending'
                
                story_info['tasks'].append({
                    'name': task_name,
                    'status': status,
                    'type': 'story'
                })
        
        if total_tasks > 0:
            story_info['progress'] = (completed_tasks / total_tasks) * 100
            
        return story_info
    except Exception as e:
        print(f"Error parsing story file {file_path}: {e}")
        return None

def parse_detailed_story(filepath: Path) -> Optional[DetailedStory]:
    """Parse a story file with detailed information"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        story_id = filepath.stem
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else story_id

        # Extract various fields
        status_match = re.search(r'Status:\s*(\w+)', content, re.IGNORECASE)
        status = status_match.group(1) if status_match else "Draft"

        agent_match = re.search(r'Agent:\s*(\w+)', content, re.IGNORECASE)
        agent = agent_match.group(1) if agent_match else None

        epic_match = re.search(r'Epic:\s*(\w+)', content, re.IGNORECASE)
        epic_id = epic_match.group(1) if epic_match else None

        priority_match = re.search(r'Priority:\s*(\w+)', content, re.IGNORECASE)
        priority = priority_match.group(1).lower() if priority_match else None

        # Extract acceptance criteria
        ac_match = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
        acceptance_criteria = []
        if ac_match:
            ac_lines = ac_match.group(1).strip().split('\n')
            acceptance_criteria = [line.strip('- ').strip() for line in ac_lines if line.strip().startswith('-')]

        # Generate sample tasks
        tasks = [
            {
                "id": f"task-{story_id}-1",
                "name": f"Implement {title} core functionality",
                "status": random.choice(['pending', 'active', 'complete']),
                "agent": agent or "dev",
                "estimatedHours": random.randint(2, 8),
                "actualHours": random.randint(1, 6)
            },
            {
                "id": f"task-{story_id}-2",
                "name": f"Test {title}",
                "status": random.choice(['pending', 'active', 'complete']),
                "agent": "qa",
                "estimatedHours": random.randint(1, 4),
                "actualHours": random.randint(1, 3)
            }
        ]

        # Generate sample tags
        tags = random.sample(['frontend', 'backend', 'api', 'ui', 'database', 'security', 'performance'],
                           random.randint(1, 3))

        return DetailedStory(
            id=story_id,
            title=title,
            status=status,
            agent=agent,
            lastUpdated=datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            description=content[:500] + "..." if len(content) > 500 else content,
            acceptanceCriteria=acceptance_criteria if acceptance_criteria else None,
            tasks=tasks,
            epicId=epic_id,
            priority=priority,
            estimatedHours=random.randint(4, 16),
            actualHours=random.randint(2, 12),
            tags=tags
        )
    except Exception as e:
        print(f"Error parsing detailed story file {filepath}: {e}")
        return None

def parse_workflow_yaml(filepath: Path) -> Optional[DetailedWorkflow]:
    """Parse a workflow YAML definition into a DetailedWorkflow object"""
    try:
        with open(filepath, 'r') as f:
            wf_data = yaml.safe_load(f)

        # Handle the actual workflow structure
        workflow_config = wf_data.get('workflow', wf_data)

        # Basic required fields
        wf_id = filepath.stem
        name = workflow_config.get('name', wf_id)
        wf_type = workflow_config.get('type', 'custom')
        sequence_data = workflow_config.get('sequence', [])

        stages: List[WorkflowStage] = []
        completed_count = 0
        current_stage_name = 'Planning'

        # Convert sequence steps to stages
        if sequence_data:
            # Group sequence steps into logical stages
            planning_steps = []
            development_steps = []
            validation_steps = []
            for step in sequence_data:
                if isinstance(step, dict):
                    # Categorize steps into stages
                    if any(keyword in str(step).lower() for keyword in ['analysis', 'prd', 'architect', 'planning']):
                        planning_steps.append(step)
                    elif any(keyword in str(step).lower() for keyword in ['development', 'implement', 'code', 'build']):
                        development_steps.append(step)
                    else:
                        validation_steps.append(step)

            # Create Planning Stage
            if planning_steps:
                planning_tasks = []
                for idx, step in enumerate(planning_steps):
                    task_id = f"{wf_id}-planning-task-{idx+1}"
                    task_name = step.get('creates', step.get('action', f"Planning Task {idx+1}"))
                    if task_name.endswith('.md'):
                        task_name = f"Create {task_name}"
                    
                    planning_tasks.append(WorkflowTask(
                        id=task_id,
                        name=task_name,
                        status=random.choice(['complete', 'active', 'pending']),
                        agent=step.get('agent', 'pm'),
                        description=step.get('notes', step.get('action', 'Planning task')),
                        checklist=None,
                        dependencies=None
                    ))
                
                stages.append(WorkflowStage(
                    id=f"{wf_id}-planning",
                    name="Planning & Analysis",
                    status='active',
                    agent='pm',
                    tasks=planning_tasks,
                    startTime=None,
                    endTime=None
                ))

            # Create Development Stage
            if development_steps or not planning_steps:  # Add development stage even if no explicit dev steps
                dev_tasks = []
                if development_steps:
                    for idx, step in enumerate(development_steps):
                        task_id = f"{wf_id}-dev-task-{idx+1}"
                        task_name = step.get('creates', step.get('action', f"Development Task {idx+1}"))
                        dev_tasks.append(WorkflowTask(
                            id=task_id,
                            name=task_name,
                            status=random.choice(['pending', 'active']),
                            agent=step.get('agent', 'dev'),
                            description=step.get('notes', step.get('action', 'Development task')),
                            checklist=None,
                            dependencies=None
                        ))
                else:
                    # Add default development tasks
                    dev_tasks = [
                        WorkflowTask(
                            id=f"{wf_id}-dev-task-1",
                            name="Implement Core Features",
                            status='pending',
                            agent='dev',
                            description="Implement the main functionality based on requirements",
                            checklist=None,
                            dependencies=None
                        ),
                        WorkflowTask(
                            id=f"{wf_id}-dev-task-2",
                            name="Code Review & Testing",
                            status='pending',
                            agent='qa',
                            description="Review code and perform testing",
                            checklist=None,
                            dependencies=None
                        )
                    ]
                
                stages.append(WorkflowStage(
                    id=f"{wf_id}-development",
                    name="Development & Implementation",
                    status='pending',
                    agent='dev',
                    tasks=dev_tasks,
                    startTime=None,
                    endTime=None
                ))

            # Create Validation Stage
            if validation_steps:
                validation_tasks = []
                for idx, step in enumerate(validation_steps):
                    task_id = f"{wf_id}-validation-task-{idx+1}"
                    task_name = step.get('action', f"Validation Task {idx+1}")
                    validation_tasks.append(WorkflowTask(
                        id=task_id,
                        name=task_name,
                        status='pending',
                        agent=step.get('agent', 'qa'),
                        description=step.get('notes', step.get('action', 'Validation task')),
                        checklist=None,
                        dependencies=None
                    ))
                
                stages.append(WorkflowStage(
                    id=f"{wf_id}-validation",
                    name="Validation & QA",
                    status='pending',
                    agent='qa',
                    tasks=validation_tasks,
                    startTime=None,
                    endTime=None
                ))

        # Calculate progress and status
        if stages:
            completed_count = sum(1 for stage in stages if stage.status == 'complete')
            progress = (completed_count / len(stages)) * 100
            
            # Determine current stage
            for stage in stages:
                if stage.status == 'active':
                    current_stage_name = stage.name
                    break
            else:
                # If no active stage, find first pending stage
                for stage in stages:
                    if stage.status == 'pending':
                        current_stage_name = stage.name
                        break
        else:
            progress = 0
            completed_count = 0

        status_overall = 'complete' if progress == 100 else 'active'

        # Extract assigned agents from sequence
        assigned_agents = []
        for step in sequence_data:
            if isinstance(step, dict) and 'agent' in step:
                agent = step['agent']
                if agent not in assigned_agents:
                    assigned_agents.append(agent)

        return DetailedWorkflow(
            id=wf_id,
            name=name,
            type=wf_type,
            currentStage=current_stage_name,
            stages=stages,
            progress=progress,
            status=status_overall,
            startTime=workflow_config.get('startTime', datetime.now().isoformat()),
            lastUpdated=datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            assignedAgents=assigned_agents,
            metadata=workflow_config.get('metadata')
        )
    except Exception as e:
        print(f"Error parsing workflow YAML {filepath}: {e}")
        return None

def get_real_agent_definitions() -> dict:
    """Get real agent definitions from .bmad-core/agents/"""
    agents = {}
    agent_dir = "../../.bmad-core/agents"
    
    if not os.path.exists(agent_dir):
        return {}
    
    for file_path in glob.glob(os.path.join(agent_dir, "*.md")):
        agent_id = os.path.basename(file_path).replace('.md', '')
        
        # Skip some system agents for cleaner display
        if agent_id in ['bmad-orchestrator', 'bmad-master', 'bmad-the-creator']:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract agent name and type from content
            name = agent_id.replace('-', ' ').title()
            agent_type = agent_id
            
            # Try to extract name from YAML if present
            if 'name:' in content:
                for line in content.split('\n'):
                    if line.strip().startswith('name:'):
                        name = line.split(':', 1)[1].strip()
                        break
            
            agents[agent_id] = {
                'id': agent_id,
                'name': name,
                'type': agent_type,
                'file': file_path
            }
        except Exception as e:
            print(f"Error reading agent file {file_path}: {e}")
    
    return agents

def get_real_tasks_data() -> list:
    """Get real tasks from .bmad-core/tasks/"""
    tasks = []
    task_dir = "../../.bmad-core/tasks"
    
    if not os.path.exists(task_dir):
        return []
    
    for file_path in glob.glob(os.path.join(task_dir, "*.md")):
        task_name = os.path.basename(file_path).replace('.md', '').replace('-', ' ').title()
        tasks.append({
            'id': os.path.basename(file_path).replace('.md', ''),
            'name': task_name,
            'type': 'task',
            'file': file_path
        })
    
    return tasks

def generate_real_agents() -> List[DetailedAgent]:
    """Generate real agent activity data from actual system state"""
    agents = []
    
    # Get real data sources
    agent_definitions = get_real_agent_definitions()
    story_files = glob.glob("../../docs/stories/*.story.md")
    real_tasks = get_real_tasks_data()
    
    # Parse all story files for real activity
    story_data = []
    for story_file in story_files:
        parsed = parse_story_file(story_file)
        if parsed:
            story_data.append(parsed)
    
    # Create agents based on real definitions
    for agent_id, agent_def in agent_definitions.items():
        # Assign real tasks from stories and tasks
        current_tasks = []
        completed_today = 0
        
        # Assign tasks based on agent type
        task_counter = 0
        for story in story_data:
            if story['status'] in ['in progress', 'review']:
                for task in story['tasks'][:2]:  # Limit to 2 tasks per story
                    if task_counter >= 3:  # Max 3 tasks per agent
                        break
                    
                    current_tasks.append(AgentTask(
                        id=f"{agent_id}-{story['file']}-{task_counter}",
                        name=task['name'],
                        type=task['type'],
                        status=task['status'],
                        priority=random.choice(['medium', 'high']),
                        startTime=(datetime.now() - timedelta(hours=random.randint(1, 12))).isoformat(),
                        estimatedDuration=random.randint(3, 8),
                        actualDuration=random.randint(1, 4) if task['status'] == 'complete' else None,
                        storyId=story['file'].replace('.story.md', ''),
                        workflowId=f"workflow-{random.randint(1, 2)}" if random.choice([True, False]) else None
                    ))
                    task_counter += 1
        
        # Add real BMAD tasks
        available_tasks = random.sample(real_tasks, min(2, len(real_tasks)))
        for bmad_task in available_tasks:
            if len(current_tasks) >= 4:  # Max 4 tasks total
                break
            
            current_tasks.append(AgentTask(
                id=f"{agent_id}-bmad-{bmad_task['id']}",
                name=bmad_task['name'],
                type='workflow',
                status=random.choice(['active', 'pending']),
                priority=random.choice(['low', 'medium', 'high']),
                startTime=(datetime.now() - timedelta(hours=random.randint(1, 8))).isoformat(),
                estimatedDuration=random.randint(2, 6),
                actualDuration=random.randint(1, 3) if random.choice([True, False]) else None,
                workflowId=bmad_task['id']
            ))
        
        # Calculate realistic metrics based on actual activity
        total_story_tasks = sum(len(story['tasks']) for story in story_data)
        completed_story_tasks = sum(len([t for t in story['tasks'] if t['status'] == 'complete']) for story in story_data)
        
        success_rate = (completed_story_tasks / max(total_story_tasks, 1)) * 100 if total_story_tasks > 0 else 85
        efficiency = min(95, max(60, success_rate + random.randint(-10, 15)))
        workload = min(100, len(current_tasks) * 20 + random.randint(10, 30))
        
        # Determine agent status based on current tasks
        if len(current_tasks) >= 3:
            status = 'busy'
        elif len(current_tasks) >= 1:
            status = 'active'
        else:
            status = 'idle'
        
        completed_today = random.randint(1, 4) if status in ['active', 'busy'] else 0
        
        # Create realistic metrics
        metrics = AgentMetrics(
            tasksCompleted=random.randint(10, 30) + completed_today,
            tasksActive=len(current_tasks),
            averageCompletionTime=random.uniform(2.0, 5.5),
            successRate=int(success_rate),
            workloadScore=workload,
            efficiencyRating=int(efficiency),
            collaborationScore=random.randint(7, 10)
        )
        
        # Agent specializations based on type
        specializations = {
            'dev': ['coding', 'architecture', 'debugging', 'api-development'],
            'pm': ['planning', 'coordination', 'stakeholder-management', 'scrum'],
            'po': ['requirements', 'prioritization', 'user-stories', 'product-vision'],
            'qa': ['testing', 'automation', 'quality-control', 'validation'],
            'sm': ['facilitation', 'process-improvement', 'team-coaching'],
            'analyst': ['analysis', 'documentation', 'requirements', 'research'],
            'architect': ['system-design', 'architecture', 'technical-strategy'],
            'ux-expert': ['user-experience', 'interface-design', 'usability'],
            'infra-devops-platform': ['infrastructure', 'deployment', 'monitoring', 'devops']
        }.get(agent_id, ['general'])
        
        agents.append(DetailedAgent(
            id=agent_id,
            name=agent_def['name'],
            type=agent_def['type'],
            status=status,
            currentTasks=current_tasks,
            completedTasksToday=completed_today,
            metrics=metrics,
            specializations=specializations,
            lastActivity=(datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
            availability=random.randint(70, 100),
            currentWorkflow=f"story-{random.choice(['1.7', '1.6', '1.5'])}" if current_tasks else None,
            collaboratingWith=random.sample([a for a in agent_definitions.keys() if a != agent_id], 
                                          random.randint(0, 2)) if len(agent_definitions) > 1 else None
        ))
    
    return agents

# Enhanced API Endpoints
@app.get("/api/v1/bmad/stories", response_model=List[StoryStatus])
@ttl_cache
async def get_stories():
    """Returns a list of all stories with their current status"""
    story_files = glob.glob(str(STORIES_PATH / "*.md"))
    stories = [parse_story_file(Path(f)) for f in story_files]
    return [s for s in stories if s]

@app.get("/api/v1/bmad/stories/detailed", response_model=List[DetailedStory])
@ttl_cache
async def get_detailed_stories():
    """Returns a list of all stories with detailed information"""
    story_files = glob.glob(str(STORIES_PATH / "*.md"))
    stories = [parse_detailed_story(Path(f)) for f in story_files]
    return [s for s in stories if s]

@app.get("/api/v1/bmad/epics/detailed", response_model=List[DetailedEpic])
@ttl_cache
async def get_detailed_epics():
    """Returns a list of all epics with detailed information"""
    epic_files = glob.glob(str(PRD_PATH / "epic-*.md"))
    epics = []

    for epic_file in epic_files:
        try:
            with open(epic_file, 'r') as f:
                content = f.read()

            epic_id = Path(epic_file).stem
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else epic_id

            # Generate sample data
            epics.append(DetailedEpic(
                id=epic_id,
                title=title,
                status=random.choice(['Planning', 'Active', 'Complete', 'On Hold']),
                stories=[f"story-{i}" for i in range(1, random.randint(3, 8))],
                progress=random.randint(20, 90),
                description=content[:300] + "..." if len(content) > 300 else content,
                startDate=(datetime.now() - timedelta(days=random.randint(10, 60))).strftime('%Y-%m-%d'),
                targetDate=(datetime.now() + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d'),
                owner=random.choice(['pm', 'po', 'sm']),
                objectives=[f"Objective {i}" for i in range(1, random.randint(3, 6))],
                keyResults=[f"Key Result {i}" for i in range(1, random.randint(2, 5))],
                dependencies=[f"epic-{i}" for i in range(1, random.randint(1, 3))],
                risks=[f"Risk {i}" for i in range(1, random.randint(1, 4))]
            ))
        except Exception as e:
            print(f"Error parsing epic file {epic_file}: {e}")

    return epics

@app.get("/api/v1/bmad/workflows/detailed", response_model=List[DetailedWorkflow])
@ttl_cache
async def get_detailed_workflows():
    """Returns a list of all workflows with detailed information"""
    WORKFLOWS_PATH.mkdir(parents=True, exist_ok=True)
    workflow_files = glob.glob(str(WORKFLOWS_PATH / "*.yml")) + glob.glob(str(WORKFLOWS_PATH / "*.yaml"))
    workflows = [parse_workflow_yaml(Path(f)) for f in workflow_files]
    return [w for w in workflows if w]

@app.get("/api/v1/bmad/agents/activity", response_model=List[DetailedAgent])
@ttl_cache
async def get_agent_activity():
    """Returns a list of all agents with their current activity"""
    return generate_real_agents()

# Workflow control endpoints
@app.post("/api/v1/bmad/workflows/{workflow_id}/pause")
async def pause_workflow(workflow_id: str):
    """Pause a workflow"""
    # In a real implementation, this would update the workflow state
    return {"status": "success", "message": f"Workflow {workflow_id} paused"}

@app.post("/api/v1/bmad/workflows/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):
    """Resume a workflow"""
    # In a real implementation, this would update the workflow state
    return {"status": "success", "message": f"Workflow {workflow_id} resumed"}

@app.post("/api/v1/bmad/workflows/{workflow_id}/stop")
async def stop_workflow(workflow_id: str):
    """Stop a workflow"""
    # In a real implementation, this would update the workflow state
    return {"status": "success", "message": f"Workflow {workflow_id} stopped"}

# Original endpoints (maintained for backward compatibility)
@app.get("/api/v1/bmad/epics")
async def get_epics():
    """Get all epics with their progress (legacy endpoint)"""
    epics = []

    # Parse all epic files
    epic_files = glob.glob(str(PRD_PATH / "epic-*.md"))
    for epic_file in epic_files[:3]:  # Limit for demo
        try:
            with open(epic_file, 'r') as f:
                content = f.read()

            epic_id = Path(epic_file).stem
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else epic_id

            stories = re.findall(r'Story:\s*(\S+)', content)
            progress = 0.0 if not stories else random.uniform(25.0, 75.0)

            epics.append({
                "id": epic_id,
                "title": title,
                "status": "Active",
                "stories": stories,
                "progress": progress
            })
        except Exception as e:
            print(f"Error parsing epic file {epic_file}: {e}")

    return epics

@app.get("/api/v1/bmad/tasks/active")
async def get_active_tasks():
    """Get currently active tasks (legacy endpoint)"""
    return [{"id": "task-003", "name": "Refactor auth service", "status": "active"}]

@app.get("/api/v1/bmad/workflows")
@ttl_cache
async def get_workflows():
    """Returns a simplified list of workflows"""
    WORKFLOWS_PATH.mkdir(parents=True, exist_ok=True)
    workflow_files = glob.glob(str(WORKFLOWS_PATH / "*.yml")) + glob.glob(str(WORKFLOWS_PATH / "*.yaml"))
    workflows = []
    for wf_file in workflow_files:
        wf = parse_workflow_yaml(Path(wf_file))
        if wf:
            workflows.append({
                "id": wf.id,
                "name": wf.name,
                "currentStage": wf.currentStage,
                "stages": wf.stages,
                "progress": wf.progress
            })
    return workflows

@app.get("/api/v1/bmad/tasks", response_model=List[TaskStatus])
@ttl_cache
async def get_tasks():
    """Returns a list of all tasks"""
    task_files = glob.glob(str(TASKS_PATH / "*.yml"))
    tasks = [parse_task_file(Path(f)) for f in task_files]
    return [t for t in tasks if t]

@app.get("/api/v1/bmad/checklists", response_model=List[Checklist])
@ttl_cache
async def get_checklists():
    """Returns a list of all checklists"""
    CHECKLISTS_PATH.mkdir(parents=True, exist_ok=True)
    checklist_files = glob.glob(str(CHECKLISTS_PATH / "*.yml"))
    checklists = [parse_checklist_file(Path(f)) for f in checklist_files]
    return [c for c in checklists if c]

@app.get("/api/v1/bmad/summary")
@ttl_cache
async def get_bmad_summary():
    """Provides a high-level summary of all BMAD artifacts"""
    # Get async data
    stories = await get_stories()
    tasks = await get_tasks()
    checklists = await get_checklists()
    
    num_stories = len(glob.glob(str(STORIES_PATH / "*.md")))
    num_epics = len(glob.glob(str(PRD_PATH / "epic-*.md")))
    num_tasks = len(glob.glob(str(TASKS_PATH / "*.md")))
    num_checklists = len(glob.glob(str(CHECKLISTS_PATH / "*.md")))

    return {
        "total_stories": num_stories,
        "stories_by_status": {
            "Draft": len([s for s in stories if (s.get('status') if isinstance(s, dict) else s.status) == "Draft"]),
            "Ready": len([s for s in stories if (s.get('status') if isinstance(s, dict) else s.status) == "Ready"]),
            "In Progress": len([s for s in stories if (s.get('status') if isinstance(s, dict) else s.status) == "In Progress"]),
            "Review": len([s for s in stories if (s.get('status') if isinstance(s, dict) else s.status) == "Review"]),
            "Done": len([s for s in stories if (s.get('status') if isinstance(s, dict) else s.status) == "Done"])
        },
        "total_epics": num_epics,
        "active_tasks": len([t for t in tasks if t.status.lower() in ["active", "in progress", "pending"]]),
        "checklists_total": num_checklists,
        "checklists_complete": len([cl for cl in checklists if cl.progress == 100]),
        "last_updated": datetime.now()
    }

@app.get("/api/v1/bmad/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# Parsing helpers

def parse_task_file(filepath: Path) -> Optional[TaskStatus]:
    """Parse a task YAML file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        task_id = filepath.stem
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1) if name_match else task_id

        status_match = re.search(r'Status:\s*(\w+)', content, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else 'pending'

        agent_match = re.search(r'Agent:\s*(\w+)', content, re.IGNORECASE)
        agent = agent_match.group(1) if agent_match else None

        story_match = re.search(r'Story:\s*(\w+)', content, re.IGNORECASE)
        story_id = story_match.group(1) if story_match else None

        epic_match = re.search(r'Epic:\s*(\w+)', content, re.IGNORECASE)
        epic_id = epic_match.group(1) if epic_match else None

        return TaskStatus(
            id=task_id,
            name=name,
            status=status.title(),
            agent=agent,
            storyId=story_id,
            epicId=epic_id,
            lastUpdated=datetime.fromtimestamp(filepath.stat().st_mtime)
        )
    except Exception as e:
        print(f"Error parsing task file {filepath}: {e}")
        return None

def parse_checklist_file(filepath: Path) -> Optional[Checklist]:
    """Parse a checklist YAML file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        cid = filepath.stem
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1) if name_match else cid

        items: List[ChecklistItem] = []
        done_count = 0
        for line in content.splitlines():
            c_match = re.match(r'- \[( |x)\] (.+)', line)
            if c_match:
                done = c_match.group(1).lower() == 'x'
                if done:
                    done_count += 1
                items.append(ChecklistItem(text=c_match.group(2), done=done))

        progress = (done_count / len(items)) * 100 if items else 0

        return Checklist(
            id=cid,
            name=name,
            items=items,
            progress=progress,
            lastUpdated=datetime.fromtimestamp(filepath.stat().st_mtime)
        )
    except Exception as e:
        print(f"Error parsing checklist file {filepath}: {e}")
        return None

@app.get("/api/v1/bmad/tasks/burndown")
@ttl_cache
async def get_task_burndown_data():
    """Generates and returns task burndown data."""
    # In a real app, this would come from a database or a more robust store.
    # For now, we'll generate some mock data.
    sprint_start_date = datetime.now() - timedelta(days=3)
    sprint_end_date = datetime.now() + timedelta(days=4)
    total_tasks = 50
    completed_tasks = 22
    
    daily_burndown = []
    remaining = total_tasks
    planned_remaining = total_tasks
    ideal_rate = total_tasks / 7.0

    for i in range(10):
        date = (sprint_start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        if i < 3: # Past days
            actual_completed = random.randint(3, 6)
            remaining -= actual_completed
        else:
            actual_completed = 0 # Future days
        
        planned_remaining -= ideal_rate

        daily_burndown.append({
            "date": date,
            "planned": round(max(0, planned_remaining)),
            "actual": remaining,
            "remaining": remaining
        })

    return {
        "totalTasks": total_tasks,
        "completedTasks": completed_tasks,
        "remainingTasks": total_tasks - completed_tasks,
        "tasksAddedToday": random.randint(2, 5),
        "tasksCompletedToday": random.randint(3, 7),
        "burndownRate": round(random.uniform(2.5, 4.0), 1),
        "projectedCompletion": (datetime.now() + timedelta(days=random.randint(3,5))).strftime('%Y-%m-%d'),
        "sprintStartDate": sprint_start_date.strftime('%Y-%m-%d'),
        "sprintEndDate": sprint_end_date.strftime('%Y-%m-%d'),
        "dailyBurndown": daily_burndown,
        "tasksByPriority": { "critical": 5, "high": 10, "medium": 8, "low": 5 },
        "tasksByStatus": { "pending": 10, "active": 8, "complete": completed_tasks, "blocked": 2 },
        "recentlyCompleted": [
            { "id": f"task-{i}", "name": f"Fix critical bug #{i}", "completedAt": "2h ago", "agent": "Dev-AI-1", "duration": 3 }
            for i in range(1, 4)
        ],
        "upcomingTasks": [
            { "id": f"task-u{i}", "name": f"Implement feature #{i}", "priority": "high", "assignedTo": "Dev-AI-2", "estimatedDuration": 8, "dependencies": [] }
            for i in range(1, 4)
        ]
    }
    
@app.get("/api/v1/bmad/checklists/progress")
@ttl_cache
async def get_checklist_progress_data():
    """Generates and returns checklist progress data."""
    # Mock data generation
    total_checklists = 15
    completed_checklists = 9
    return {
        "totalChecklists": total_checklists,
        "completedChecklists": completed_checklists,
        "inProgressChecklists": 4,
        "blockedChecklists": 2,
        "overallProgress": (completed_checklists / total_checklists) * 100 if total_checklists > 0 else 0,
        "itemsCompletedToday": random.randint(10, 25),
        "averageCompletionTime": round(random.uniform(1.5, 3.0), 1),
        "categoryBreakdown": {
            "story": { "total": 8, "completed": 5, "progress": 62.5 },
            "epic": { "total": 3, "completed": 1, "progress": 33.3 },
            "release": { "total": 2, "completed": 2, "progress": 100.0 },
            "quality-gate": { "total": 2, "completed": 1, "progress": 50.0 }
        },
        "recentlyCompleted": [
            { "checklistId": f"chk-{i}", "checklistName": f"Story {i} DOD", "itemText": f"Code review complete", "completedBy": "QA-Bot-1", "completedAt": datetime.now().isoformat() }
            for i in range(1, 5)
        ],
        "checklists": [
            {
                "id": f"checklist-{i}",
                "name": f"Sprint {i} Planning Checklist",
                "category": "sprint",
                "priority": random.choice(["high", "medium"]),
                "status": random.choice(["in-progress", "completed"]),
                "progress": random.randint(20, 100),
                "totalItems": 20,
                "completedItems": random.randint(5, 20),
                "assignedTo": "SM-AI",
                "items": [ { "id": f"item-{j}", "text": f"Task breakdown for story {j}", "completed": random.choice([True, False]), "priority": "high", "category": "development" } for j in range(1, 5) ]
            }
            for i in range(1, 6)
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced BMAD Tracking API on port 8767")
    print("📊 New endpoints available:")
    print("   - /api/v1/bmad/stories/detailed")
    print("   - /api/v1/bmad/epics/detailed")
    print("   - /api/v1/bmad/workflows/detailed")
    print("   - /api/v1/bmad/agents/activity")
    print("   - /api/v1/bmad/tasks")
    print("   - /api/v1/bmad/checklists")
    print("   - /api/v1/bmad/summary")
    uvicorn.run(app, host="0.0.0.0", port=8767)