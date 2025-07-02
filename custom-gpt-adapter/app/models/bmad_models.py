import uuid
import enum
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Float, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

# Enums for BMAD system
class AgentStatus(enum.Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    OFFLINE = "offline"
    PAUSED = "paused"

class AgentType(enum.Enum):
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    ARCHITECT = "architect"
    TESTER = "tester"
    CUSTOM = "custom"

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

class WorkflowType(enum.Enum):
    GREENFIELD_FULLSTACK = "greenfield-fullstack"
    BROWNFIELD_FULLSTACK = "brownfield-fullstack"
    GREENFIELD_SERVICE = "greenfield-service"
    BROWNFIELD_SERVICE = "brownfield-service"
    GREENFIELD_UI = "greenfield-ui"
    BROWNFIELD_UI = "brownfield-ui"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StoryStatus(enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"

class ChecklistItemType(enum.Enum):
    REQUIREMENT = "requirement"
    QUALITY_GATE = "quality_gate"
    VERIFICATION = "verification"
    DOCUMENTATION = "documentation"

# Core BMAD Agent Models
class BMadAgent(Base):
    __tablename__ = "bmad_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, unique=True, index=True, nullable=False)  # e.g., 'dev', 'pm', 'qa'
    name = Column(String, nullable=False)  # Human-friendly name
    title = Column(String)  # Professional title
    icon = Column(String)  # Emoji or icon
    agent_type = Column(String, nullable=False)  # developer, project_manager, etc.

    # Agent state
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    current_session_id = Column(String)
    current_user_id = Column(String)
    
    # Agent configuration
    specializations = Column(ARRAY(String), default=list)  # Technical specializations
    available_commands = Column(JSON, default=list)  # Available commands/tools
    dependencies = Column(JSON, default=dict)  # Required tasks, templates, etc.
    when_to_use = Column(Text)  # Clear usage criteria
    
    # Performance metrics
    total_tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # 0-100
    average_task_duration = Column(Float, default=0.0)  # hours
    efficiency_score = Column(Float, default=0.0)  # 0-100
    
    # Current assignments
    current_workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"), nullable=True)
    current_story_id = Column(UUID(as_uuid=True), ForeignKey("bmad_stories.id"), nullable=True)
    workload_capacity = Column(Integer, default=100)  # 0-100 percentage
    
    # Context and memory integration
    memory_context = Column(JSON, default=dict)  # Current memory context
    context_categories = Column(ARRAY(String), default=list)  # Memory categories used
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    assigned_tasks = relationship("BMadTask", foreign_keys="BMadTask.assigned_agent_id", back_populates="assigned_agent")
    current_workflow = relationship("BMadWorkflow", foreign_keys=[current_workflow_id], back_populates="active_agents")
    activity_logs = relationship("BMadAgentActivity", back_populates="agent", cascade="all, delete-orphan")

class BMadWorkflow(Base):
    __tablename__ = "bmad_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String, unique=True, index=True, nullable=False)  # greenfield-fullstack, etc.
    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_type = Column(Enum(WorkflowType), nullable=False)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    
    # Configuration
    project_types = Column(ARRAY(String), default=list)
    sequence = Column(JSON, nullable=False)  # workflow sequence configuration
    metadata = Column(JSON, default=dict)
    
    # Progress tracking
    current_stage = Column(String)
    stages = Column(JSON, default=list)  # stage definitions and progress
    progress_percentage = Column(Float, default=0.0)
    
    # Timeline
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    estimated_duration = Column(Float)  # in hours
    actual_duration = Column(Float)  # in hours
    
    # Context
    user_id = Column(String)  # user who initiated
    session_id = Column(String)
    parent_epic_id = Column(UUID(as_uuid=True), ForeignKey("bmad_epics.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    tasks = relationship("BMadTask", back_populates="workflow", cascade="all, delete-orphan")
    stories = relationship("BMadStory", back_populates="workflow")
    active_agents = relationship("BMadAgent", foreign_keys="BMadAgent.current_workflow_id", back_populates="current_workflow")
    stages_detail = relationship("BMadWorkflowStage", back_populates="workflow", cascade="all, delete-orphan")
    parent_epic = relationship("BMadEpic", back_populates="workflows")

class BMadWorkflowStage(Base):
    __tablename__ = "bmad_workflow_stages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"), nullable=False)
    stage_id = Column(String, nullable=False)  # planning, development, validation
    name = Column(String, nullable=False)
    description = Column(Text)
    sequence_order = Column(Integer, nullable=False)
    
    # Status and progress
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    
    # Agent assignment
    primary_agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"))
    assigned_agents = Column(ARRAY(String), default=list)  # agent IDs
    
    # Timeline
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    estimated_duration = Column(Float)
    actual_duration = Column(Float)
    
    # Configuration
    prerequisites = Column(JSON, default=list)  # required dependencies
    deliverables = Column(JSON, default=list)  # expected outputs
    quality_gates = Column(JSON, default=list)  # validation criteria
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    workflow = relationship("BMadWorkflow", back_populates="stages_detail")
    primary_agent = relationship("BMadAgent", foreign_keys=[primary_agent_id])
    tasks = relationship("BMadTask", back_populates="stage")

class BMadTask(Base):
    __tablename__ = "bmad_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, index=True, nullable=False)  # user-friendly ID
    name = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String)  # create-doc, execute-checklist, etc.
    
    # Status and priority
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Assignment
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"))
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"))
    stage_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflow_stages.id"))
    story_id = Column(UUID(as_uuid=True), ForeignKey("bmad_stories.id"), nullable=True)
    
    # Dependencies and relationships
    dependencies = Column(JSON, default=list)  # task IDs this depends on
    blocks = Column(JSON, default=list)  # task IDs this blocks
    template_used = Column(String)  # template file used
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("bmad_checklists.id"), nullable=True)
    
    # Timeline and effort
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    due_date = Column(DateTime)
    
    # Output and results
    output_files = Column(JSON, default=list)  # generated files/documents
    output_data = Column(JSON, default=dict)  # structured output data
    quality_score = Column(Float)  # 0-100 quality rating
    
    # Context
    session_id = Column(String)
    user_id = Column(String)
    input_parameters = Column(JSON, default=dict)  # parameters used for execution
    execution_log = Column(JSON, default=list)  # execution steps and log
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    assigned_agent = relationship("BMadAgent", foreign_keys=[assigned_agent_id], back_populates="assigned_tasks")
    workflow = relationship("BMadWorkflow", back_populates="tasks")
    stage = relationship("BMadWorkflowStage", back_populates="tasks")
    story = relationship("BMadStory", back_populates="tasks")
    checklist = relationship("BMadChecklist", back_populates="tasks")

class BMadStory(Base):
    __tablename__ = "bmad_stories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(String, unique=True, index=True, nullable=False)  # 1.1, 1.2, etc.
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(StoryStatus), default=StoryStatus.DRAFT)
    
    # Assignment and workflow
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"))
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"))
    epic_id = Column(UUID(as_uuid=True), ForeignKey("bmad_epics.id"))
    
    # Story details
    user_story = Column(Text)  # As a... I want... So that...
    acceptance_criteria = Column(JSON, default=list)
    definition_of_done = Column(JSON, default=list)
    business_value = Column(Text)
    
    # Estimation and tracking
    story_points = Column(Integer)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Timeline
    start_date = Column(DateTime)
    target_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Dependencies
    dependencies = Column(JSON, default=list)  # story IDs this depends on
    blocks = Column(JSON, default=list)  # story IDs this blocks
    
    # Metadata
    tags = Column(ARRAY(String), default=list)
    labels = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    assigned_agent = relationship("BMadAgent", foreign_keys=[assigned_agent_id])
    workflow = relationship("BMadWorkflow", back_populates="stories")
    epic = relationship("BMadEpic", back_populates="stories")
    tasks = relationship("BMadTask", back_populates="story")

class BMadEpic(Base):
    __tablename__ = "bmad_epics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    epic_id = Column(String, unique=True, index=True, nullable=False)  # epic-1, epic-2, etc.
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(StoryStatus), default=StoryStatus.DRAFT)
    
    # Epic metadata
    theme = Column(String)  # overarching theme
    business_objective = Column(Text)
    success_criteria = Column(JSON, default=list)
    kpis = Column(JSON, default=list)  # key performance indicators
    
    # Timeline and estimation
    start_date = Column(DateTime)
    target_date = Column(DateTime)
    estimated_duration = Column(Float)  # in weeks
    actual_duration = Column(Float)  # in weeks
    
    # Priority and value
    business_value = Column(Integer)  # 1-100
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Progress tracking
    total_stories = Column(Integer, default=0)
    completed_stories = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    
    # Context
    project_id = Column(String)
    stakeholders = Column(ARRAY(String), default=list)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    stories = relationship("BMadStory", back_populates="epic", cascade="all, delete-orphan")
    workflows = relationship("BMadWorkflow", back_populates="parent_epic")

class BMadChecklist(Base):
    __tablename__ = "bmad_checklists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    checklist_type = Column(String)  # architect, pm, qa, etc.
    
    # Checklist items
    items = Column(JSON, nullable=False)  # list of checklist items
    completion_status = Column(JSON, default=dict)  # item_id: boolean
    
    # Usage tracking
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Context
    template_file = Column(String)  # source template file
    created_by_agent = Column(String)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    tasks = relationship("BMadTask", back_populates="checklist")

class BMadAgentActivity(Base):
    __tablename__ = "bmad_agent_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String, nullable=False)  # task_start, task_complete, workflow_join, etc.
    activity_data = Column(JSON)  # structured activity data
    command = Column(String)  # command executed, if any
    
    # Context
    session_id = Column(String)
    user_id = Column(String)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("bmad_tasks.id"), nullable=True)
    
    # Performance metrics
    response_time = Column(Float)  # seconds
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Memory integration
    memory_context_used = Column(JSON)  # memory context that was used
    memory_created = Column(JSON)  # new memories created during activity
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relationships
    agent = relationship("BMadAgent", back_populates="activity_logs")
    workflow = relationship("BMadWorkflow")
    task = relationship("BMadTask")

class BMadAgentCollaboration(Base):
    __tablename__ = "bmad_agent_collaborations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    primary_agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"), nullable=False)
    collaborating_agent_id = Column(UUID(as_uuid=True), ForeignKey("bmad_agents.id"), nullable=False)
    
    # Collaboration details
    collaboration_type = Column(String)  # handoff, parallel, review, consultation
    context = Column(String)  # what they're collaborating on
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("bmad_workflows.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("bmad_tasks.id"), nullable=True)
    
    # Timeline
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Float)  # hours
    
    # Quality metrics
    success_rating = Column(Float)  # 0-100
    handoff_quality = Column(Float)  # 0-100
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    primary_agent = relationship("BMadAgent", foreign_keys=[primary_agent_id])
    collaborating_agent = relationship("BMadAgent", foreign_keys=[collaborating_agent_id])
    workflow = relationship("BMadWorkflow")
    task = relationship("BMadTask")

class BMadMemoryIntegration(Base):
    __tablename__ = "bmad_memory_integration"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Memory system integration
    memory_service_id = Column(String)  # ID from memory service
    bmad_entity_type = Column(String, nullable=False)  # agent, workflow, task, story
    bmad_entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Memory categories and context
    memory_category = Column(String)  # AGENT_CONTEXT, WORKFLOW_PATTERNS, etc.
    context_type = Column(String)  # preference, technical, project, workflow
    relevance_score = Column(Float, default=0.0)
    
    # Usage tracking
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    created_context = Column(JSON)  # context when memory was created
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 