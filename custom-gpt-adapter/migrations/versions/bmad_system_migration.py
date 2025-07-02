"""BMAD System Migration

Revision ID: bmad_system_001
Revises: 97c83b94b9c4
Create Date: 2024-12-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bmad_system_001'
down_revision: Union[str, None] = '97c83b94b9c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include BMAD system tables."""
    
    # Create BMAD enums
    agent_status_enum = postgresql.ENUM(
        'idle', 'active', 'busy', 'offline', 'paused',
        name='agentstatus'
    )
    agent_status_enum.create(op.get_bind())
    
    workflow_status_enum = postgresql.ENUM(
        'draft', 'active', 'paused', 'completed', 'cancelled', 'error',
        name='workflowstatus'
    )
    workflow_status_enum.create(op.get_bind())
    
    task_status_enum = postgresql.ENUM(
        'pending', 'active', 'in_progress', 'review', 'completed', 'blocked', 'cancelled',
        name='taskstatus'
    )
    task_status_enum.create(op.get_bind())
    
    task_priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='taskpriority'
    )
    task_priority_enum.create(op.get_bind())
    
    story_status_enum = postgresql.ENUM(
        'draft', 'ready', 'in_progress', 'review', 'done', 'cancelled',
        name='storystatus'
    )
    story_status_enum.create(op.get_bind())
    
    workflow_type_enum = postgresql.ENUM(
        'greenfield-fullstack', 'brownfield-fullstack', 'greenfield-service',
        'brownfield-service', 'greenfield-ui', 'brownfield-ui',
        name='workflowtype'
    )
    workflow_type_enum.create(op.get_bind())
    
    # Create BMAD epics table
    op.create_table('bmad_epics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('epic_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'ready', 'in_progress', 'review', 'done', 'cancelled', name='storystatus'), nullable=True),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('business_objective', sa.Text(), nullable=True),
        sa.Column('success_criteria', sa.JSON(), nullable=True),
        sa.Column('kpis', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Float(), nullable=True),
        sa.Column('actual_duration', sa.Float(), nullable=True),
        sa.Column('business_value', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='taskpriority'), nullable=True),
        sa.Column('total_stories', sa.Integer(), nullable=True),
        sa.Column('completed_stories', sa.Integer(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('stakeholders', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_epics_epic_id'), 'bmad_epics', ['epic_id'], unique=True)
    
    # Create BMAD workflows table
    op.create_table('bmad_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workflow_type', sa.Enum('greenfield-fullstack', 'brownfield-fullstack', 'greenfield-service', 'brownfield-service', 'greenfield-ui', 'brownfield-ui', name='workflowtype'), nullable=False),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', 'cancelled', 'error', name='workflowstatus'), nullable=True),
        sa.Column('project_types', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('sequence', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('current_stage', sa.String(), nullable=True),
        sa.Column('stages', sa.JSON(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Float(), nullable=True),
        sa.Column('actual_duration', sa.Float(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('parent_epic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_epic_id'], ['bmad_epics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_workflows_workflow_id'), 'bmad_workflows', ['workflow_id'], unique=True)
    
    # Create BMAD agents table
    op.create_table('bmad_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('idle', 'active', 'busy', 'offline', 'paused', name='agentstatus'), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('current_session_id', sa.String(), nullable=True),
        sa.Column('current_user_id', sa.String(), nullable=True),
        sa.Column('specializations', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('available_commands', sa.JSON(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('when_to_use', sa.Text(), nullable=True),
        sa.Column('total_tasks_completed', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('average_task_duration', sa.Float(), nullable=True),
        sa.Column('efficiency_score', sa.Float(), nullable=True),
        sa.Column('current_workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('current_story_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workload_capacity', sa.Integer(), nullable=True),
        sa.Column('memory_context', sa.JSON(), nullable=True),
        sa.Column('context_categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['current_workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_agents_agent_id'), 'bmad_agents', ['agent_id'], unique=True)
    
    # Create BMAD stories table  
    op.create_table('bmad_stories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('story_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'ready', 'in_progress', 'review', 'done', 'cancelled', name='storystatus'), nullable=True),
        sa.Column('assigned_agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('epic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_story', sa.Text(), nullable=True),
        sa.Column('acceptance_criteria', sa.JSON(), nullable=True),
        sa.Column('definition_of_done', sa.JSON(), nullable=True),
        sa.Column('business_value', sa.Text(), nullable=True),
        sa.Column('story_points', sa.Integer(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='taskpriority'), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('blocks', sa.JSON(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('labels', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['epic_id'], ['bmad_epics.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_stories_story_id'), 'bmad_stories', ['story_id'], unique=True)
    
    # Update bmad_agents foreign key for current_story_id
    op.create_foreign_key(None, 'bmad_agents', 'bmad_stories', ['current_story_id'], ['id'])
    
    # Create BMAD workflow stages table
    op.create_table('bmad_workflow_stages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'active', 'in_progress', 'review', 'completed', 'blocked', 'cancelled', name='taskstatus'), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('primary_agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_agents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Float(), nullable=True),
        sa.Column('actual_duration', sa.Float(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('deliverables', sa.JSON(), nullable=True),
        sa.Column('quality_gates', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['primary_agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create BMAD checklists table
    op.create_table('bmad_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('checklist_type', sa.String(), nullable=True),
        sa.Column('items', sa.JSON(), nullable=False),
        sa.Column('completion_status', sa.JSON(), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=True),
        sa.Column('completed_items', sa.Integer(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=True),
        sa.Column('template_file', sa.String(), nullable=True),
        sa.Column('created_by_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_checklists_checklist_id'), 'bmad_checklists', ['checklist_id'], unique=True)
    
    # Create BMAD tasks table
    op.create_table('bmad_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'active', 'in_progress', 'review', 'completed', 'blocked', 'cancelled', name='taskstatus'), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='taskpriority'), nullable=True),
        sa.Column('assigned_agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stage_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('story_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('blocks', sa.JSON(), nullable=True),
        sa.Column('template_used', sa.String(), nullable=True),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('output_files', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('input_parameters', sa.JSON(), nullable=True),
        sa.Column('execution_log', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['checklist_id'], ['bmad_checklists.id'], ),
        sa.ForeignKeyConstraint(['stage_id'], ['bmad_workflow_stages.id'], ),
        sa.ForeignKeyConstraint(['story_id'], ['bmad_stories.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_tasks_task_id'), 'bmad_tasks', ['task_id'])
    
    # Create BMAD agent activity table
    op.create_table('bmad_agent_activity',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_type', sa.String(), nullable=False),
        sa.Column('activity_data', sa.JSON(), nullable=True),
        sa.Column('command', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('memory_context_used', sa.JSON(), nullable=True),
        sa.Column('memory_created', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['bmad_tasks.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bmad_agent_activity_timestamp'), 'bmad_agent_activity', ['timestamp'])
    
    # Create BMAD agent collaborations table
    op.create_table('bmad_agent_collaborations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('primary_agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collaborating_agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collaboration_type', sa.String(), nullable=True),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('success_rating', sa.Float(), nullable=True),
        sa.Column('handoff_quality', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['collaborating_agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['primary_agent_id'], ['bmad_agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['bmad_tasks.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['bmad_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create BMAD memory integration table
    op.create_table('bmad_memory_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('memory_service_id', sa.String(), nullable=True),
        sa.Column('bmad_entity_type', sa.String(), nullable=False),
        sa.Column('bmad_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('memory_category', sa.String(), nullable=True),
        sa.Column('context_type', sa.String(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('created_context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema to remove BMAD system tables."""
    
    # Drop tables in reverse dependency order
    op.drop_table('bmad_memory_integration')
    op.drop_table('bmad_agent_collaborations')
    op.drop_index(op.f('ix_bmad_agent_activity_timestamp'), table_name='bmad_agent_activity')
    op.drop_table('bmad_agent_activity')
    op.drop_index(op.f('ix_bmad_tasks_task_id'), table_name='bmad_tasks')
    op.drop_table('bmad_tasks')
    op.drop_index(op.f('ix_bmad_checklists_checklist_id'), table_name='bmad_checklists')
    op.drop_table('bmad_checklists')
    op.drop_table('bmad_workflow_stages')
    op.drop_index(op.f('ix_bmad_stories_story_id'), table_name='bmad_stories')
    op.drop_table('bmad_stories')
    op.drop_index(op.f('ix_bmad_agents_agent_id'), table_name='bmad_agents')
    op.drop_table('bmad_agents')
    op.drop_index(op.f('ix_bmad_workflows_workflow_id'), table_name='bmad_workflows')
    op.drop_table('bmad_workflows')
    op.drop_index(op.f('ix_bmad_epics_epic_id'), table_name='bmad_epics')
    op.drop_table('bmad_epics')
    
    # Drop enums
    sa.Enum(name='workflowtype').drop(op.get_bind())
    sa.Enum(name='storystatus').drop(op.get_bind())
    sa.Enum(name='taskpriority').drop(op.get_bind())
    sa.Enum(name='taskstatus').drop(op.get_bind())
    sa.Enum(name='workflowstatus').drop(op.get_bind())
    sa.Enum(name='agentstatus').drop(op.get_bind()) 