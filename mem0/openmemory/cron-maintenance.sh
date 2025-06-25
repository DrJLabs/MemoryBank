#!/bin/bash
# Cron-compatible maintenance scheduler for Advanced Memory System
# Based on system maintenance best practices

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAINTENANCE_SCRIPT="$SCRIPT_DIR/maintenance-schedule.sh"
LOG_DIR="$SCRIPT_DIR/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Daily health check (every day at 6 AM)
daily_health() {
    echo "$(date): Running daily health check" >> "$LOG_DIR/daily.log"
    cd "$SCRIPT_DIR" && "$MAINTENANCE_SCRIPT" health >> "$LOG_DIR/daily.log" 2>&1
}

# Weekly cleanup (every Sunday at 2 AM)  
weekly_cleanup() {
    echo "$(date): Running weekly cleanup" >> "$LOG_DIR/weekly.log"
    cd "$SCRIPT_DIR" && "$MAINTENANCE_SCRIPT" cleanup >> "$LOG_DIR/weekly.log" 2>&1
}

# Monthly full maintenance (first day of month at 1 AM)
monthly_full() {
    echo "$(date): Running monthly full maintenance" >> "$LOG_DIR/monthly.log"
    cd "$SCRIPT_DIR" && "$MAINTENANCE_SCRIPT" full >> "$LOG_DIR/monthly.log" 2>&1
}

# Emergency backup (on demand)
emergency_backup() {
    echo "$(date): Running emergency backup" >> "$LOG_DIR/backup.log"
    cd "$SCRIPT_DIR" && "$MAINTENANCE_SCRIPT" backup >> "$LOG_DIR/backup.log" 2>&1
}

# Install cron jobs
install_cron() {
    echo "Installing maintenance cron jobs..."
    
    # Create temporary cron file
    TEMP_CRON=$(mktemp)
    
    # Add existing cron jobs (preserve them)
    crontab -l 2>/dev/null > "$TEMP_CRON" || true
    
    # Add memory system maintenance jobs
    cat >> "$TEMP_CRON" << EOF

# Advanced Memory System Maintenance
# Daily health check at 6 AM
0 6 * * * $SCRIPT_DIR/cron-maintenance.sh daily_health
# Weekly cleanup every Sunday at 2 AM  
0 2 * * 0 $SCRIPT_DIR/cron-maintenance.sh weekly_cleanup
# Monthly full maintenance on 1st at 1 AM
0 1 1 * * $SCRIPT_DIR/cron-maintenance.sh monthly_full

EOF
    
    # Install the cron jobs
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"
    
    echo "Cron jobs installed successfully!"
    echo "Current schedule:"
    crontab -l | grep -A4 "Memory System Maintenance"
}

# Remove cron jobs
remove_cron() {
    echo "Removing maintenance cron jobs..."
    TEMP_CRON=$(mktemp)
    crontab -l 2>/dev/null | grep -v "Memory System Maintenance" | grep -v "daily_health" | grep -v "weekly_cleanup" | grep -v "monthly_full" > "$TEMP_CRON"
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"
    echo "Cron jobs removed successfully!"
}

# Main execution
case "${1:-help}" in
    "daily_health")
        daily_health
        ;;
    "weekly_cleanup")
        weekly_cleanup
        ;;
    "monthly_full")
        monthly_full
        ;;
    "emergency_backup")
        emergency_backup
        ;;
    "install")
        install_cron
        ;;
    "remove")
        remove_cron
        ;;
    "status")
        echo "Current cron jobs for memory system:"
        crontab -l 2>/dev/null | grep -A10 "Memory System Maintenance" || echo "No maintenance cron jobs found"
        ;;
    *)
        echo "Advanced Memory System Cron Maintenance"
        echo "Usage: $0 {daily_health|weekly_cleanup|monthly_full|emergency_backup|install|remove|status}"
        echo ""
        echo "Commands:"
        echo "  install         - Install automated maintenance cron jobs"
        echo "  remove          - Remove maintenance cron jobs"  
        echo "  status          - Show current maintenance schedule"
        echo "  daily_health    - Run daily health check (called by cron)"
        echo "  weekly_cleanup  - Run weekly cleanup (called by cron)"
        echo "  monthly_full    - Run monthly full maintenance (called by cron)"
        echo "  emergency_backup - Run emergency backup"
        ;;
esac 