#!/usr/bin/env python3
"""
Demo script to generate sample monitoring data and alerts
This helps test the monitoring dashboard with realistic data
"""

import sys
import os
import sqlite3

import random
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

try:
    from monitoring_dashboard import MemorySystemMonitor
except ImportError:
    print("Warning: monitoring_dashboard.py not found, creating basic demo data")
    MemorySystemMonitor = None

def create_demo_database():
    """Create demo monitoring database with sample data"""
    db_path = Path("monitoring.db")
    
    print("📊 Creating demo monitoring database...")
    
    with sqlite3.connect(db_path) as conn:
        # Create tables if they don't exist
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
    
    print("✅ Database tables created/verified")

def generate_historical_metrics(hours=24):
    """Generate realistic historical metrics"""
    db_path = Path("monitoring.db")
    
    print(f"📈 Generating {hours} hours of historical metrics...")
    
    with sqlite3.connect(db_path) as conn:
        # Clear existing demo data
        conn.execute("DELETE FROM metrics WHERE timestamp > datetime('now', '-25 hours')")
        
        base_time = datetime.now() - timedelta(hours=hours)
        base_memory_count = 42
        
        for i in range(hours * 12):  # Every 5 minutes
            timestamp = base_time + timedelta(minutes=i * 5)
            
            # Realistic variations
            memory_count = base_memory_count + random.randint(-2, 5) + (i // 12)  # Slow growth
            api_response_time = random.uniform(0.05, 0.3) + (random.random() * 0.2 if random.random() > 0.9 else 0)
            cpu_usage = random.uniform(15, 45) + (random.random() * 30 if random.random() > 0.95 else 0)
            memory_usage = random.uniform(45, 70) + (random.random() * 20 if random.random() > 0.9 else 0)
            disk_usage = random.uniform(25, 40) + (i * 0.01)  # Slow disk growth
            
            # Occasional spikes
            if random.random() > 0.98:
                cpu_usage = random.uniform(80, 95)
                memory_usage = random.uniform(80, 90)
                api_response_time = random.uniform(1.0, 3.0)
            
            api_status = "UP" if api_response_time < 2.0 else "SLOW"
            if random.random() > 0.995:  # Rare downtime
                api_status = "DOWN"
                api_response_time = -1
            
            conn.execute("""
                INSERT INTO metrics (
                    timestamp, memory_count, api_response_time, cpu_usage,
                    memory_usage, disk_usage, docker_containers, docker_images,
                    docker_storage_mb, api_status, services_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp.isoformat(),
                memory_count,
                api_response_time,
                cpu_usage,
                memory_usage,
                disk_usage,
                random.randint(3, 6),
                random.randint(8, 12),
                random.uniform(800, 1200),
                api_status,
                '{"docker_compose": "UP"}'
            ))
    
    print(f"✅ Generated {hours * 12} metric entries")

def generate_sample_alerts():
    """Generate realistic sample alerts"""
    db_path = Path("monitoring.db")
    
    print("🚨 Generating sample alerts...")
    
    alerts = [
        {
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "level": "WARNING",
            "component": "system",
            "message": "High CPU usage: 85.2%",
            "resolved": True
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
            "level": "INFO",
            "component": "memory_system",
            "message": "Memory count reached 50 memories milestone",
            "resolved": False
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
            "level": "WARNING",
            "component": "performance",
            "message": "High API response time: 2.8s",
            "resolved": True
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=8)).isoformat(),
            "level": "CRITICAL",
            "component": "api",
            "message": "API endpoint temporarily unavailable",
            "resolved": True
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "level": "WARNING",
            "component": "system",
            "message": "Memory usage above threshold: 88.4%",
            "resolved": False
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "level": "INFO",
            "component": "docker",
            "message": "Container restart detected for memory-api",
            "resolved": False
        }
    ]
    
    with sqlite3.connect(db_path) as conn:
        # Clear existing demo alerts
        conn.execute("DELETE FROM alerts WHERE timestamp > datetime('now', '-25 hours')")
        
        for alert in alerts:
            conn.execute("""
                INSERT INTO alerts (timestamp, level, component, message, resolved)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert["timestamp"],
                alert["level"],
                alert["component"],
                alert["message"],
                alert["resolved"]
            ))
    
    print(f"✅ Generated {len(alerts)} sample alerts")

def add_real_time_metric():
    """Add one current real-time metric"""
    if MemorySystemMonitor:
        print("📊 Adding real-time metric from monitoring system...")
        monitor = MemorySystemMonitor()
        metrics = monitor.collect_system_metrics()
        monitor.store_metrics(metrics)
        print(f"✅ Real-time metric added: {metrics.memory_count} memories, {metrics.cpu_usage:.1f}% CPU")
    else:
        print("⚠️ Real monitoring system not available, using simulated data")
        db_path = Path("monitoring.db")
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (
                    timestamp, memory_count, api_response_time, cpu_usage,
                    memory_usage, disk_usage, docker_containers, docker_images,
                    docker_storage_mb, api_status, services_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                random.randint(45, 55),
                random.uniform(0.1, 0.4),
                random.uniform(20, 50),
                random.uniform(50, 75),
                random.uniform(30, 45),
                random.randint(3, 6),
                random.randint(8, 12),
                random.uniform(900, 1100),
                "UP",
                '{"docker_compose": "UP"}'
            ))
        print("✅ Simulated real-time metric added")

def main():
    """Main demo function"""
    print("🚀 Memory-C* Monitoring Dashboard Demo Data Generator")
    print("=" * 60)
    
    # Create database and tables
    create_demo_database()
    
    # Generate historical data
    generate_historical_metrics(12)  # 12 hours of data
    
    # Generate sample alerts
    generate_sample_alerts()
    
    # Add current metric
    add_real_time_metric()
    
    print("\n🎉 Demo data generation complete!")
    print("=" * 60)
    print("✅ Database: monitoring.db")
    print("✅ Historical metrics: 12 hours")
    print("✅ Sample alerts: 6 alerts")
    print("✅ Current metric: Added")
    print("\n📱 Now you can start the monitoring dashboard:")
    print("   ./start-monitoring-dashboard.sh")
    print("\n📊 The dashboard will show:")
    print("   • Real-time system health metrics")
    print("   • Memory count trends and growth")
    print("   • API performance monitoring")
    print("   • Alert notifications and history")

if __name__ == "__main__":
    main() 