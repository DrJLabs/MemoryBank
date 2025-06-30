# 🚀 BMAD Monitoring Quick Start

## Start the BMAD Monitoring System

### 1. Start the BMAD Tracking API
```bash
./mem0/openmemory/manage-bmad-api.sh start
```

### 2. Verify API is Running
```bash
./mem0/openmemory/manage-bmad-api.sh status
```

### 3. Access the Dashboard
Open your browser to: **http://localhost:3000**

## What You'll See

✅ **BMAD Project Tracking Section** with 6 monitoring cards:
- 📊 **BMAD Tracking** - Overall project statistics
- 🔄 **Workflow Tracker** - Active workflows with control buttons
- 👥 **Agent Activity** - Real-time agent workload and metrics
- 📈 **Task Burndown** - Task completion trends
- ✔️ **Checklist Progress** - Checklist completion tracking
- 📋 **Story & Epic Tracker** - Detailed story/epic information

## Troubleshooting

### ❌ If you see "Failed to fetch BMAD data":

1. **Start the API**:
   ```bash
   ./mem0/openmemory/manage-bmad-api.sh start
   ```

2. **Check API health**:
   ```bash
   curl http://localhost:8767/api/v1/bmad/health
   ```

3. **View logs**:
   ```bash
   ./mem0/openmemory/manage-bmad-api.sh logs
   ```

## Stop the API

When you're done:
```bash
./mem0/openmemory/manage-bmad-api.sh stop
```

---

💡 **Pro Tip**: The dashboard auto-refreshes every 30 seconds, but you can manually refresh the page for immediate updates. 