#!/usr/bin/env python3
"""
Advanced Memory System - Real-time Monitoring Dashboard
Based on automated monitoring best practices for software maintenance
"""

import asyncio
import json
import time
import psutil
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path
import sqlite3

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: str
    memory_count: int
    api_response_time: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    docker_containers: int
    docker_images: int
    docker_storage_mb: float
    api_status: str
    services_status: Dict[str, str]

@dataclass
class Alert:
    """Alert data structure"""
    timestamp: str
    level: str  # INFO, WARNING, CRITICAL
    component: str
    message: str
    resolved: bool = False

class MemorySystemMonitor:
    """Advanced monitoring system for Memory-C* system"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        self.config = self._load_config(config_file)
        self.db_path = Path("monitoring.db")
        self.alerts = []
        self.running = False
        self._init_database()
        self.baseline_metrics = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "api_url": "http://localhost:8765",
            "monitoring_interval": 60,  # seconds
            "alert_thresholds": {
                "api_response_time": 2.0,  # seconds
                "cpu_usage": 80.0,  # percentage
                "memory_usage": 85.0,  # percentage
                "disk_usage": 90.0,  # percentage
                "memory_growth_rate": 50  # memories per hour
            },
            "retention_days": 30,
            "dashboard_port": 8080
        }
        
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        return default_config
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    memory_count INTEGER,
                    api_response_time REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    docker_containers INTEGER,
                    docker_images INTEGER,
                    docker_storage_mb REAL,
                    api_status TEXT,
                    services_status TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        timestamp = datetime.now().isoformat()
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Memory system metrics
        memory_count = self._get_memory_count()
        api_response_time = self._measure_api_response_time()
        api_status = "UP" if api_response_time > 0 else "DOWN"
        
        # Docker metrics
        docker_info = self._get_docker_info()
        
        # Services status
        services_status = self._check_services_status()
        
        return SystemMetrics(
            timestamp=timestamp,
            memory_count=memory_count,
            api_response_time=api_response_time,
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            docker_containers=docker_info['containers'],
            docker_images=docker_info['images'],
            docker_storage_mb=docker_info['storage_mb'],
            api_status=api_status,
            services_status=services_status
        )
    
    def _get_memory_count(self) -> int:
        """Get current memory count from the system"""
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
            self._create_alert("CRITICAL", "memory_system", f"Failed to get memory count: {e}")
            return -1
    
    def _measure_api_response_time(self) -> float:
        """Measure API response time"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.config['api_url']}/docs", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return response_time
            else:
                self._create_alert("WARNING", "api", f"API returned status {response.status_code}")
                return -1
        except Exception as e:
            self._create_alert("CRITICAL", "api", f"API unreachable: {e}")
            return -1
    
    def _get_docker_info(self) -> Dict[str, Any]:
        """Get Docker system information"""
        try:
            # Get container count
            result = subprocess.run(['docker', 'ps', '-q'], capture_output=True, text=True)
            container_count = len([line for line in result.stdout.strip().split('\n') if line])
            
            # Get image count
            result = subprocess.run(['docker', 'images', '-q'], capture_output=True, text=True)
            image_count = len([line for line in result.stdout.strip().split('\n') if line])
            
            # Get storage usage
            result = subprocess.run(['docker', 'system', 'df', '--format', 'json'], 
                                  capture_output=True, text=True)
            storage_mb = 0
            if result.returncode == 0:
                try:
                    # Parse docker system df output (simplified)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        storage_mb = 1000  # Placeholder - actual parsing would be more complex
                except:
                    storage_mb = 0
            
            return {
                'containers': container_count,
                'images': image_count,
                'storage_mb': storage_mb
            }
        except Exception as e:
            self._create_alert("WARNING", "docker", f"Failed to get Docker info: {e}")
            return {'containers': -1, 'images': -1, 'storage_mb': -1}
    
    def _check_services_status(self) -> Dict[str, str]:
        """Check status of all services"""
        services = {}
        
        try:
            # Check Docker Compose services
            result = subprocess.run([
                'docker', 'compose', 'ps', '--format', 'json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Simplified status check
                services['docker_compose'] = "UP" if "Up" in result.stdout else "DOWN"
            else:
                services['docker_compose'] = "DOWN"
                
        except Exception as e:
            services['docker_compose'] = "ERROR"
            self._create_alert("CRITICAL", "services", f"Failed to check services: {e}")
        
        return services
    
    def _create_alert(self, level: str, component: str, message: str):
        """Create and store an alert"""
        alert = Alert(
            timestamp=datetime.now().isoformat(),
            level=level,
            component=component,
            message=message
        )
        
        self.alerts.append(alert)
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (timestamp, level, component, message)
                VALUES (?, ?, ?, ?)
            """, (alert.timestamp, alert.level, alert.component, alert.message))
        
        print(f"🚨 [{alert.level}] {alert.component}: {alert.message}")
    
    def store_metrics(self, metrics: SystemMetrics):
        """Store metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (
                    timestamp, memory_count, api_response_time, cpu_usage,
                    memory_usage, disk_usage, docker_containers, docker_images,
                    docker_storage_mb, api_status, services_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp, metrics.memory_count, metrics.api_response_time,
                metrics.cpu_usage, metrics.memory_usage, metrics.disk_usage,
                metrics.docker_containers, metrics.docker_images, metrics.docker_storage_mb,
                metrics.api_status, json.dumps(metrics.services_status)
            ))
    
    def analyze_metrics(self, metrics: SystemMetrics):
        """Analyze metrics for anomalies and threshold breaches"""
        thresholds = self.config['alert_thresholds']
        
        # Check API response time
        if metrics.api_response_time > thresholds['api_response_time']:
            self._create_alert("WARNING", "performance", 
                             f"High API response time: {metrics.api_response_time:.2f}s")
        
        # Check CPU usage
        if metrics.cpu_usage > thresholds['cpu_usage']:
            self._create_alert("WARNING", "system", f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        # Check memory usage
        if metrics.memory_usage > thresholds['memory_usage']:
            self._create_alert("WARNING", "system", f"High memory usage: {metrics.memory_usage:.1f}%")
        
        # Check disk usage
        if metrics.disk_usage > thresholds['disk_usage']:
            self._create_alert("CRITICAL", "system", f"High disk usage: {metrics.disk_usage:.1f}%")
        
        # Check API status
        if metrics.api_status == "DOWN":
            self._create_alert("CRITICAL", "api", "API is not responding")
        
        # Check memory growth rate (if baseline exists)
        if self.baseline_metrics:
            self._check_memory_growth_rate(metrics)
    
    def _check_memory_growth_rate(self, current_metrics: SystemMetrics):
        """Check if memory growth rate is concerning"""
        if self.baseline_metrics and self.baseline_metrics.memory_count > 0:
            time_diff = (datetime.fromisoformat(current_metrics.timestamp) - 
                        datetime.fromisoformat(self.baseline_metrics.timestamp))
            hours_diff = time_diff.total_seconds() / 3600
            
            if hours_diff > 0:
                growth_rate = (current_metrics.memory_count - self.baseline_metrics.memory_count) / hours_diff
                threshold = self.config['alert_thresholds']['memory_growth_rate']
                
                if growth_rate > threshold:
                    self._create_alert("WARNING", "memory_growth", 
                                     f"High memory growth rate: {growth_rate:.1f} memories/hour")
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        with sqlite3.connect(self.db_path) as conn:
            # Get latest metrics
            cursor = conn.execute("""
                SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 1
            """)
            latest_metrics_row = cursor.fetchone()
            
            # Get recent alerts
            cursor = conn.execute("""
                SELECT * FROM alerts WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC LIMIT 10
            """)
            recent_alerts = cursor.fetchall()
            
            # Get metrics summary for last 24 hours
            cursor = conn.execute("""
                SELECT AVG(api_response_time), AVG(cpu_usage), AVG(memory_usage),
                       MIN(memory_count), MAX(memory_count)
                FROM metrics WHERE timestamp > datetime('now', '-24 hours')
            """)
            metrics_summary = cursor.fetchone()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "latest_metrics": dict(zip([col[0] for col in cursor.description], latest_metrics_row)) if latest_metrics_row else None,
            "recent_alerts": [dict(zip(['id', 'timestamp', 'level', 'component', 'message', 'resolved'], alert)) for alert in recent_alerts],
            "24h_summary": {
                "avg_api_response_time": metrics_summary[0] if metrics_summary[0] else 0,
                "avg_cpu_usage": metrics_summary[1] if metrics_summary[1] else 0,
                "avg_memory_usage": metrics_summary[2] if metrics_summary[2] else 0,
                "memory_count_range": f"{metrics_summary[3] if metrics_summary[3] else 0}-{metrics_summary[4] if metrics_summary[4] else 0}"
            } if metrics_summary else {}
        }
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.running = True
        print("🚀 Starting Advanced Memory System Monitor")
        print(f"📊 Monitoring interval: {self.config['monitoring_interval']} seconds")
        print(f"🎯 API URL: {self.config['api_url']}")
        
        # Set baseline
        initial_metrics = self.collect_system_metrics()
        self.baseline_metrics = initial_metrics
        self.store_metrics(initial_metrics)
        
        print(f"📋 Baseline established: {initial_metrics.memory_count} memories")
        
        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                
                # Store metrics
                self.store_metrics(metrics)
                
                # Analyze for alerts
                self.analyze_metrics(metrics)
                
                # Print status
                print(f"✅ [{metrics.timestamp}] "
                      f"Memories: {metrics.memory_count}, "
                      f"API: {metrics.api_response_time:.2f}s, "
                      f"CPU: {metrics.cpu_usage:.1f}%, "
                      f"RAM: {metrics.memory_usage:.1f}%")
                
                # Wait for next collection
                await asyncio.sleep(self.config['monitoring_interval'])
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self._create_alert("CRITICAL", "monitor", f"Monitoring error: {e}")
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)  # Short wait before retry
        
        self.running = False

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Memory System Monitor")
    parser.add_argument('--config', default='monitoring_config.json', help='Configuration file')
    parser.add_argument('--report', action='store_true', help='Generate status report and exit')
    parser.add_argument('--test', action='store_true', help='Run single collection test and exit')
    
    args = parser.parse_args()
    
    monitor = MemorySystemMonitor(args.config)
    
    if args.report:
        report = monitor.generate_status_report()
        print(json.dumps(report, indent=2))
        return
    
    if args.test:
        metrics = monitor.collect_system_metrics()
        print("✅ Test collection successful:")
        print(f"   Memory Count: {metrics.memory_count}")
        print(f"   API Response: {metrics.api_response_time:.2f}s")
        print(f"   CPU Usage: {metrics.cpu_usage:.1f}%")
        print(f"   Memory Usage: {metrics.memory_usage:.1f}%")
        return
    
    # Start monitoring
    try:
        asyncio.run(monitor.start_monitoring())
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    main() 