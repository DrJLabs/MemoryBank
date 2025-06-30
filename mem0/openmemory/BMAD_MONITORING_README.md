# BMAD Monitoring Dashboard

## Overview

The BMAD monitoring features provide real-time tracking and visualization of your BMAD project's progress, including stories, epics, tasks, workflows, agent activity, and checklists.

## Components

### 1. **BMADTrackingCard**
- Shows overall project statistics
- Displays story status breakdown (Draft, Ready, In Progress, Review, Done)
- Shows active tasks count and checklist completion

### 2. **WorkflowTracker**
- Real-time workflow progress visualization
- Stage-by-stage tracking with task details
- Workflow control buttons (pause/resume/stop)

### 3. **StoryEpicTracker**
- Comprehensive view of all stories and epics
- Expandable cards with detailed information
- Progress tracking and status indicators

### 4. **AgentActivityTracker**
- Live agent status and workload monitoring
- Performance metrics for each agent
- Task assignment visualization

### 5. **TaskBurndownCard**
- Task completion trends over time
- Burndown chart visualization
- Active/pending/completed task breakdown

### 6. **ChecklistProgressCard**
- Checklist completion tracking
- Progress bars for each checklist
- Quick overview of pending items

## Setup and Usage

### Starting the BMAD Tracking API

The monitoring features require the BMAD tracking API to be running. Use the management script:

```bash
# Start the API
./mem0/openmemory/manage-bmad-api.sh start

# Check status
./mem0/openmemory/manage-bmad-api.sh status

# View logs
./mem0/openmemory/manage-bmad-api.sh logs

# Stop the API
./mem0/openmemory/manage-bmad-api.sh stop

# Restart the API
./mem0/openmemory/manage-bmad-api.sh restart
```

### API Endpoints

The BMAD API runs on port 8767 and provides the following endpoints:

- `GET /api/v1/bmad/health` - Health check
- `GET /api/v1/bmad/summary` - Overall project summary
- `GET /api/v1/bmad/stories` - List all stories
- `GET /api/v1/bmad/stories/detailed` - Detailed story information
- `GET /api/v1/bmad/epics` - List all epics
- `GET /api/v1/bmad/epics/detailed` - Detailed epic information
- `GET /api/v1/bmad/workflows` - Workflow states
- `GET /api/v1/bmad/workflows/detailed` - Detailed workflow information
- `GET /api/v1/bmad/agents/activity` - Agent activity and metrics
- `GET /api/v1/bmad/tasks` - All tasks
- `GET /api/v1/bmad/tasks/active` - Active tasks only
- `GET /api/v1/bmad/checklists` - All checklists with progress

### Workflow Control Endpoints

- `POST /api/v1/bmad/workflows/{workflow_id}/pause` - Pause a workflow
- `POST /api/v1/bmad/workflows/{workflow_id}/resume` - Resume a workflow
- `POST /api/v1/bmad/workflows/{workflow_id}/stop` - Stop a workflow

## Data Sources

The BMAD tracking API reads data from:

1. **Stories**: `docs/stories/*.md`
2. **Epics**: `docs/prd/epic-*.md`
3. **Workflows**: `.bmad-core/workflows/*.yml`
4. **Tasks**: `.bmad-core/tasks/*.md`
5. **Checklists**: `.bmad-core/checklists/*.md`
6. **Agents**: Generated mock data (can be replaced with real agent data)

## Troubleshooting

### Components show "Failed to fetch BMAD data"

1. Check if the API is running:
   ```bash
   ./mem0/openmemory/manage-bmad-api.sh status
   ```

2. If not running, start it:
   ```bash
   ./mem0/openmemory/manage-bmad-api.sh start
   ```

3. Check the logs for errors:
   ```bash
   ./mem0/openmemory/manage-bmad-api.sh logs
   ```

### API fails to start

1. Check Python dependencies:
   ```bash
   pip install fastapi uvicorn pyyaml pydantic
   ```

2. Check if port 8767 is already in use:
   ```bash
   netstat -tuln | grep 8767
   ```

3. Check file permissions and paths

### Data not updating

1. Ensure your BMAD files are in the correct directories
2. Check file formats match expected patterns
3. Refresh the page or wait for the 30-second auto-refresh

## Development

### Adding New Metrics

To add new metrics to the dashboard:

1. Update the API endpoints in `bmad-tracking-api.py`
2. Create new React components in `ui/components/dashboard/`
3. Import and add components to `ui/app/page.tsx`
4. Follow the existing pattern for data fetching with axios

### Customizing Update Intervals

Each component has a configurable refresh interval. Default is 30 seconds. To change:

```typescript
// In any dashboard component
useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Change to 60 seconds
    return () => clearInterval(interval);
}, []);
```

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Historical data tracking and trends
- [ ] Export functionality for reports
- [ ] Integration with external project management tools
- [ ] Customizable dashboard layouts
- [ ] Alert notifications for critical events
- [ ] Performance optimization for large projects 