# 🚀 Quick Maintenance Reference

## Daily Commands (Copy-Paste Ready)

### Health Check
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
./maintenance-schedule.sh health
```

### Weekly Cleanup  
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
./maintenance-schedule.sh cleanup
```

### Emergency Backup
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
./maintenance-schedule.sh backup
```

### Full Maintenance
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
./maintenance-schedule.sh full
```

## Automated Setup

### Install Cron Jobs (One-time)
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
./cron-maintenance.sh install
```

### Check Cron Status
```bash
./cron-maintenance.sh status
```

## Quick Diagnostics

### System Analytics
```bash
cd /home/drj/*C-System/Memory-C*
python3 mem0/openmemory/advanced-memory-ai.py analytics
```

### Docker Resource Usage
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
docker system df
```

### Service Status
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
docker-compose ps
```

## Maintenance Schedule

| Frequency | Time | Command | Purpose |
|-----------|------|---------|---------|
| Daily | 6 AM | `health` | Service monitoring |
| Weekly | Sun 2 AM | `cleanup` | Resource optimization |
| Monthly | 1st 1 AM | `full` | Complete maintenance |
| On-demand | Manual | `backup` | Emergency backup |

## Troubleshooting

### Services Down
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
docker-compose down && docker-compose up -d
```

### Clear Everything (Nuclear Option)
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
docker-compose down -v
docker system prune -af
./maintenance-schedule.sh full
```

### Check Logs
```bash
cd /home/drj/*C-System/Memory-C*/mem0/openmemory
ls -la logs/
tail -f logs/maintenance.log
``` 