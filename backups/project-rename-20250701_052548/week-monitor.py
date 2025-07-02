#!/usr/bin/env python3
"""
Advanced Memory System - Initial Week Monitoring
Following automated monitoring best practices for the first week
"""

import asyncio
import json
import time
import psutil
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import logging

class WeekOneMonitor:
    """Simplified monitoring system for initial week validation"""
    
    def __init__(self):
        self.config = {
            "api_url": "http://localhost:8765",
            "monitoring_interval": 300,  # 5 minutes for initial week
            "alert_thresholds": {
                "api_response_time": 2.0,
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0
            }
        }
        
        self.db_path = Path("week_monitor.db")
        self.setup_logging()
        self.init_database()
        
    def setup_logging(self):
        """Setup logging for monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('week_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize monitoring database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS week_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    memory_count INTEGER,
                    api_response_time REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    status TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS week_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT DEFAULT 'INFO'
                )
            """)
    
    def collect_metrics(self) -> dict:
        """Collect system metrics"""
        timestamp = datetime.now().isoformat()
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Memory system metrics
        memory_count = self.get_memory_count()
        api_response_time = self.measure_api_response()
        
        # Overall status
        status = "HEALTHY"
        if api_response_time < 0:
            status = "API_DOWN"
        elif api_response_time > self.config['alert_thresholds']['api_response_time']:
            status = "SLOW_API"
        elif cpu_usage > self.config['alert_thresholds']['cpu_usage']:
            status = "HIGH_CPU"
        elif memory.percent > self.config['alert_thresholds']['memory_usage']:
            status = "HIGH_MEMORY"
        elif disk.percent > self.config['alert_thresholds']['disk_usage']:
            status = "HIGH_DISK"
        
        return {
            'timestamp': timestamp,
            'memory_count': memory_count,
            'api_response_time': api_response_time,
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'status': status
        }
    
    def get_memory_count(self) -> int:
        """Get current memory count"""
        try:
            result = subprocess.run([
                'python3', 'advanced-memory-ai.py', 'analytics'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Total Memories:' in line:
                        return int(line.split(':')[1].strip())
            return -1
        except Exception as e:
            self.log_event("ERROR", f"Failed to get memory count: {e}")
            return -1
    
    def measure_api_response(self) -> float:
        """Measure API response time"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.config['api_url']}/docs", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return response_time
            else:
                self.log_event("WARNING", f"API returned status {response.status_code}")
                return -1
        except Exception as e:
            self.log_event("ERROR", f"API unreachable: {e}")
            return -1
    
    def store_metrics(self, metrics: dict):
        """Store metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO week_metrics (
                    timestamp, memory_count, api_response_time, cpu_usage,
                    memory_usage, disk_usage, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics['timestamp'], metrics['memory_count'], 
                metrics['api_response_time'], metrics['cpu_usage'],
                metrics['memory_usage'], metrics['disk_usage'], 
                metrics['status']
            ))
    
    def log_event(self, severity: str, description: str):
        """Log an event"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO week_events (timestamp, event_type, description, severity)
                VALUES (?, ?, ?, ?)
            """, (timestamp, severity, description, severity))
        
        if severity == "ERROR":
            self.logger.error(description)
        elif severity == "WARNING":
            self.logger.warning(description)
        else:
            self.logger.info(description)
    
    def check_alerts(self, metrics: dict):
        """Check for alert conditions"""
        alerts = []
        
        if metrics['api_response_time'] > self.config['alert_thresholds']['api_response_time']:
            alerts.append(f"High API response time: {metrics['api_response_time']:.2f}s")
        
        if metrics['cpu_usage'] > self.config['alert_thresholds']['cpu_usage']:
            alerts.append(f"High CPU usage: {metrics['cpu_usage']:.1f}%")
        
        if metrics['memory_usage'] > self.config['alert_thresholds']['memory_usage']:
            alerts.append(f"High memory usage: {metrics['memory_usage']:.1f}%")
        
        if metrics['disk_usage'] > self.config['alert_thresholds']['disk_usage']:
            alerts.append(f"High disk usage: {metrics['disk_usage']:.1f}%")
        
        if metrics['api_response_time'] < 0:
            alerts.append("API is not responding")
        
        for alert in alerts:
            self.log_event("WARNING", alert)
            # Send desktop notification if possible
            try:
                subprocess.run([
                    'notify-send', 'Memory-C* Alert', alert, '-t', '5000'
                ], check=False)
            except:
                pass  # Desktop notifications not available
        
        return alerts
    
    async def start_monitoring(self, duration_hours: int = None):
        """Start monitoring for specified duration"""
        self.logger.info("🚀 Starting Week One Memory System Monitor")
        self.logger.info(f"📊 Monitoring interval: {self.config['monitoring_interval']} seconds")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours) if duration_hours else None
        
        self.log_event("INFO", "Week One monitoring started")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Store metrics
                self.store_metrics(metrics)
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                
                # Log current status
                status_emoji = {
                    "HEALTHY": "✅",
                    "API_DOWN": "❌",
                    "SLOW_API": "⚠️",
                    "HIGH_CPU": "🔥",
                    "HIGH_MEMORY": "💾",
                    "HIGH_DISK": "💿"
                }.get(metrics['status'], "📊")
                
                alert_info = f" ({len(alerts)} alerts)" if alerts else ""
                
                self.logger.info(f"{status_emoji} [{metrics['timestamp']}] "
                               f"Status: {metrics['status']}, "
                               f"Memories: {metrics['memory_count']}, "
                               f"API: {metrics['api_response_time']:.2f}s, "
                               f"CPU: {metrics['cpu_usage']:.1f}%, "
                               f"RAM: {metrics['memory_usage']:.1f}%"
                               f"{alert_info}")
                
                # Check if monitoring duration is complete
                if end_time and datetime.now() >= end_time:
                    self.logger.info(f"✅ Monitoring duration complete ({duration_hours}h)")
                    break
                
                # Wait for next collection
                await asyncio.sleep(self.config['monitoring_interval'])
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)  # Wait before retry
        
        self.log_event("INFO", "Week One monitoring stopped")
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report"""
        self.logger.info("📋 Generating Week One Summary Report...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Get metrics summary
            cursor = conn.execute("""
                SELECT COUNT(*), AVG(api_response_time), AVG(cpu_usage), 
                       AVG(memory_usage), MIN(memory_count), MAX(memory_count),
                       COUNT(CASE WHEN status != 'HEALTHY' THEN 1 END) as issues
                FROM week_metrics
            """)
            stats = cursor.fetchone()
            
            # Get recent events
            cursor = conn.execute("""
                SELECT COUNT(*) as total, severity
                FROM week_events
                GROUP BY severity
                ORDER BY severity
            """)
            events = cursor.fetchall()
            
        report = {
            "monitoring_period": "Week One Monitoring",
            "total_measurements": stats[0] if stats[0] else 0,
            "average_api_response": f"{stats[1]:.2f}s" if stats[1] else "N/A",
            "average_cpu_usage": f"{stats[2]:.1f}%" if stats[2] else "N/A",
            "average_memory_usage": f"{stats[3]:.1f}%" if stats[3] else "N/A",
            "memory_count_range": f"{stats[4]}-{stats[5]}" if stats[4] and stats[5] else "N/A",
            "system_issues": stats[6] if stats[6] else 0,
            "events_by_severity": dict(events) if events else {}
        }
        
        self.logger.info("📊 Week One Summary:")
        self.logger.info(f"   Total measurements: {report['total_measurements']}")
        self.logger.info(f"   Avg API response: {report['average_api_response']}")
        self.logger.info(f"   System issues: {report['system_issues']}")
        self.logger.info(f"   Memory range: {report['memory_count_range']}")
        
        # Save detailed report
        with open('week_one_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info("💾 Detailed report saved to week_one_report.json")

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Week One Memory System Monitor")
    parser.add_argument('--hours', type=int, help='Monitoring duration in hours')
    parser.add_argument('--test', action='store_true', help='Run single test measurement')
    parser.add_argument('--report', action='store_true', help='Generate summary report')
    
    args = parser.parse_args()
    
    monitor = WeekOneMonitor()
    
    if args.test:
        metrics = monitor.collect_metrics()
        print("✅ Test measurement:")
        print(f"   Status: {metrics['status']}")
        print(f"   Memories: {metrics['memory_count']}")
        print(f"   API Response: {metrics['api_response_time']:.2f}s")
        print(f"   CPU: {metrics['cpu_usage']:.1f}%")
        print(f"   Memory: {metrics['memory_usage']:.1f}%")
        return
    
    if args.report:
        monitor.generate_summary_report()
        return
    
    # Start monitoring
    try:
        asyncio.run(monitor.start_monitoring(args.hours))
    except KeyboardInterrupt:
        print("\n👋 Week One monitoring stopped")

if __name__ == "__main__":
    main() 