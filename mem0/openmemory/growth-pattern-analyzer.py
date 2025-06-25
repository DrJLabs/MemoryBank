#!/usr/bin/env python3
"""
Advanced Memory System - Growth Pattern Analysis & Long-term Optimization
Analyzes memory usage patterns, performance trends, and provides optimization recommendations
"""

import json
import sqlite3
import time
import statistics
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import requests
import psutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class GrowthPatternAnalyzer:
    """Comprehensive growth pattern analysis and optimization system"""
    
    def __init__(self, config_file: str = "growth_analysis_config.json"):
        self.config = self._load_config(config_file)
        self.analysis_db = Path("growth_analysis.db")
        self.api_url = "http://localhost:8765"
        self.reports_dir = Path("growth_reports")
        
        self.setup_logging()
        self.init_database()
        self.ensure_directories()
        
    def setup_logging(self):
        """Setup logging for growth analysis"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('growth_analysis.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load growth analysis configuration"""
        default_config = {
            "analysis_period_days": 30,
            "memory_growth_threshold": 0.1,  # 10% growth rate trigger
            "performance_degradation_threshold": 0.2,  # 20% slower trigger
            "resource_utilization_threshold": 0.8,  # 80% resource usage trigger
            "optimization_intervals": {
                "daily_analysis": True,
                "weekly_deep_analysis": True,
                "monthly_capacity_planning": True
            },
            "trend_analysis": {
                "min_data_points": 7,
                "confidence_threshold": 0.8,
                "prediction_horizon_days": 90
            },
            "alert_thresholds": {
                "memory_count_spike": 100,
                "api_response_time_ms": 1000,
                "disk_usage_percent": 85,
                "memory_usage_percent": 85
            }
        }
        
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        return default_config
    
    def init_database(self):
        """Initialize growth analysis database"""
        with sqlite3.connect(self.analysis_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    memory_count INTEGER,
                    api_response_time_ms REAL,
                    memory_types TEXT,
                    system_cpu_percent REAL,
                    system_memory_percent REAL,
                    disk_usage_percent REAL,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    trend_direction TEXT,
                    confidence_score REAL,
                    analysis_period_days INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    impact_score REAL,
                    implementation_effort TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS capacity_projections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    projection_date TEXT NOT NULL,
                    projected_memory_count INTEGER,
                    projected_storage_mb REAL,
                    projected_api_response_time_ms REAL,
                    confidence_level REAL,
                    projection_horizon_days INTEGER
                )
            """)
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.reports_dir.mkdir(exist_ok=True)
        (self.reports_dir / "charts").mkdir(exist_ok=True)
    
    def collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system and memory metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "memory_count": 0,
            "api_response_time_ms": 0,
            "memory_types": "{}",
            "system_cpu_percent": psutil.cpu_percent(interval=1),
            "system_memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('.').percent,
            "collection_errors": []
        }
        
        try:
            # Collect memory count and API response time
            start_time = time.time()
            response = requests.get(f"{self.api_url}/api/v1/memories", timeout=5)
            api_response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                memory_data = response.json()
                metrics["memory_count"] = len(memory_data.get("memories", []))
                metrics["api_response_time_ms"] = api_response_time
                
                # Analyze memory types
                memory_types = defaultdict(int)
                for memory in memory_data.get("memories", []):
                    memory_type = memory.get("category", "general")
                    memory_types[memory_type] += 1
                
                metrics["memory_types"] = json.dumps(dict(memory_types))
            else:
                metrics["collection_errors"].append(f"API error: {response.status_code}")
                
        except requests.RequestException as e:
            metrics["collection_errors"].append(f"API connection error: {e}")
            self.logger.error(f"Failed to collect API metrics: {e}")
        
        except Exception as e:
            metrics["collection_errors"].append(f"Metrics collection error: {e}")
            self.logger.error(f"Metrics collection error: {e}")
        
        return metrics
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in database"""
        with sqlite3.connect(self.analysis_db) as conn:
            conn.execute("""
                INSERT INTO memory_metrics (
                    timestamp, memory_count, api_response_time_ms, memory_types,
                    system_cpu_percent, system_memory_percent, disk_usage_percent, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics["timestamp"],
                metrics["memory_count"],
                metrics["api_response_time_ms"],
                metrics["memory_types"],
                metrics["system_cpu_percent"],
                metrics["system_memory_percent"],
                metrics["disk_usage_percent"],
                json.dumps(metrics.get("collection_errors", []))
            ))
    
    def analyze_growth_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze growth trends over specified period"""
        self.logger.info(f"📈 Analyzing growth trends over {days} days...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.analysis_db) as conn:
            cursor = conn.execute("""
                SELECT timestamp, memory_count, api_response_time_ms, 
                       system_cpu_percent, system_memory_percent, disk_usage_percent
                FROM memory_metrics 
                WHERE timestamp >= ? 
                ORDER BY timestamp
            """, (start_date.isoformat(),))
            
            data = cursor.fetchall()
        
        if len(data) < self.config["trend_analysis"]["min_data_points"]:
            return {
                "status": "insufficient_data",
                "data_points": len(data),
                "required_points": self.config["trend_analysis"]["min_data_points"]
            }
        
        # Extract time series data
        timestamps = [datetime.fromisoformat(row[0]) for row in data]
        memory_counts = [row[1] for row in data if row[1] is not None]
        api_times = [row[2] for row in data if row[2] is not None]
        cpu_usage = [row[3] for row in data if row[3] is not None]
        memory_usage = [row[4] for row in data if row[4] is not None]
        disk_usage = [row[5] for row in data if row[5] is not None]
        
        trends = {}
        
        # Analyze memory growth trend
        if memory_counts:
            memory_trend = self._calculate_trend(memory_counts)
            trends["memory_count"] = {
                "current": memory_counts[-1],
                "initial": memory_counts[0],
                "growth_rate": memory_trend["slope"],
                "growth_percentage": ((memory_counts[-1] - memory_counts[0]) / memory_counts[0] * 100) if memory_counts[0] > 0 else 0,
                "trend_direction": memory_trend["direction"],
                "confidence": memory_trend["confidence"]
            }
        
        # Analyze API performance trend
        if api_times:
            api_trend = self._calculate_trend(api_times)
            trends["api_performance"] = {
                "current_ms": api_times[-1],
                "initial_ms": api_times[0],
                "performance_change": api_trend["slope"],
                "trend_direction": api_trend["direction"],
                "confidence": api_trend["confidence"]
            }
        
        # Analyze system resource trends
        if cpu_usage:
            cpu_trend = self._calculate_trend(cpu_usage)
            trends["cpu_usage"] = {
                "current_percent": cpu_usage[-1],
                "average_percent": statistics.mean(cpu_usage),
                "trend_direction": cpu_trend["direction"],
                "confidence": cpu_trend["confidence"]
            }
        
        if memory_usage:
            memory_trend = self._calculate_trend(memory_usage)
            trends["system_memory"] = {
                "current_percent": memory_usage[-1],
                "average_percent": statistics.mean(memory_usage),
                "trend_direction": memory_trend["direction"],
                "confidence": memory_trend["confidence"]
            }
        
        if disk_usage:
            disk_trend = self._calculate_trend(disk_usage)
            trends["disk_usage"] = {
                "current_percent": disk_usage[-1],
                "average_percent": statistics.mean(disk_usage),
                "trend_direction": disk_trend["direction"],
                "confidence": disk_trend["confidence"]
            }
        
        # Store trend analysis
        self._store_trends(trends, days)
        
        return {
            "status": "success",
            "analysis_period_days": days,
            "data_points": len(data),
            "trends": trends,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend statistics for a series of values"""
        if len(values) < 2:
            return {"slope": 0, "direction": "stable", "confidence": 0}
        
        # Simple linear regression
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Calculate slope
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Determine trend direction
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Calculate confidence (correlation coefficient)
        if len(values) > 2:
            try:
                correlation = np.corrcoef(x, values)[0, 1]
                confidence = abs(correlation) if not np.isnan(correlation) else 0
            except:
                confidence = 0
        else:
            confidence = 0
        
        return {
            "slope": slope,
            "direction": direction,
            "confidence": confidence
        }
    
    def _store_trends(self, trends: Dict[str, Any], analysis_period: int):
        """Store trend analysis results"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.analysis_db) as conn:
            for metric_name, trend_data in trends.items():
                if isinstance(trend_data, dict) and "trend_direction" in trend_data:
                    conn.execute("""
                        INSERT INTO performance_trends (
                            timestamp, metric_name, metric_value, trend_direction,
                            confidence_score, analysis_period_days
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp,
                        metric_name,
                        trend_data.get("current", 0),
                        trend_data["trend_direction"],
                        trend_data.get("confidence", 0),
                        analysis_period
                    ))
    
    def generate_capacity_projections(self, horizon_days: int = 90) -> Dict[str, Any]:
        """Generate capacity projections based on current trends"""
        self.logger.info(f"🔮 Generating capacity projections for {horizon_days} days...")
        
        # Get recent trend data
        trend_analysis = self.analyze_growth_trends(30)
        
        if trend_analysis["status"] != "success":
            return {"status": "failed", "reason": "insufficient_trend_data"}
        
        trends = trend_analysis["trends"]
        projections = {}
        
        # Project memory count growth
        if "memory_count" in trends:
            memory_data = trends["memory_count"]
            current_count = memory_data["current"]
            growth_rate = memory_data["growth_rate"]
            confidence = memory_data["confidence"]
            
            projected_count = max(0, current_count + (growth_rate * horizon_days))
            
            projections["memory_count"] = {
                "current": current_count,
                "projected": int(projected_count),
                "growth_rate_per_day": growth_rate,
                "confidence": confidence,
                "projection_date": (datetime.now() + timedelta(days=horizon_days)).isoformat()
            }
        
        # Project API performance
        if "api_performance" in trends:
            api_data = trends["api_performance"]
            current_time = api_data["current_ms"]
            performance_change = api_data["performance_change"]
            confidence = api_data["confidence"]
            
            projected_time = max(1, current_time + (performance_change * horizon_days))
            
            projections["api_response_time"] = {
                "current_ms": current_time,
                "projected_ms": projected_time,
                "performance_change_per_day": performance_change,
                "confidence": confidence
            }
        
        # Project storage requirements (estimate based on memory count)
        if "memory_count" in projections:
            avg_memory_size_kb = 2.5  # Estimated average memory size
            current_storage = projections["memory_count"]["current"] * avg_memory_size_kb / 1024  # MB
            projected_storage = projections["memory_count"]["projected"] * avg_memory_size_kb / 1024  # MB
            
            projections["storage_requirements"] = {
                "current_mb": current_storage,
                "projected_mb": projected_storage,
                "growth_mb": projected_storage - current_storage
            }
        
        # Store projections
        self._store_projections(projections, horizon_days)
        
        return {
            "status": "success",
            "projection_horizon_days": horizon_days,
            "projections": projections,
            "projection_timestamp": datetime.now().isoformat()
        }
    
    def _store_projections(self, projections: Dict[str, Any], horizon_days: int):
        """Store capacity projections"""
        timestamp = datetime.now().isoformat()
        projection_date = (datetime.now() + timedelta(days=horizon_days)).isoformat()
        
        with sqlite3.connect(self.analysis_db) as conn:
            conn.execute("""
                INSERT INTO capacity_projections (
                    timestamp, projection_date, projected_memory_count,
                    projected_storage_mb, projected_api_response_time_ms,
                    confidence_level, projection_horizon_days
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                projection_date,
                projections.get("memory_count", {}).get("projected", 0),
                projections.get("storage_requirements", {}).get("projected_mb", 0),
                projections.get("api_response_time", {}).get("projected_ms", 0),
                projections.get("memory_count", {}).get("confidence", 0),
                horizon_days
            ))
    
    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on analysis"""
        self.logger.info("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Get current metrics
        current_metrics = self.collect_current_metrics()
        
        # Get recent trends
        trend_analysis = self.analyze_growth_trends(30)
        
        # Check for immediate issues
        if current_metrics["memory_count"] > self.config["alert_thresholds"]["memory_count_spike"]:
            recommendations.append({
                "category": "memory_management",
                "priority": "high",
                "recommendation": f"Consider implementing memory archival strategy. Current count: {current_metrics['memory_count']}",
                "impact_score": 0.8,
                "implementation_effort": "medium"
            })
        
        if current_metrics["api_response_time_ms"] > self.config["alert_thresholds"]["api_response_time_ms"]:
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "recommendation": f"API response time degraded: {current_metrics['api_response_time_ms']:.1f}ms. Consider optimization.",
                "impact_score": 0.9,
                "implementation_effort": "high"
            })
        
        if current_metrics["disk_usage_percent"] > self.config["alert_thresholds"]["disk_usage_percent"]:
            recommendations.append({
                "category": "storage",
                "priority": "high",
                "recommendation": f"Disk usage high: {current_metrics['disk_usage_percent']:.1f}%. Implement cleanup strategy.",
                "impact_score": 0.9,
                "implementation_effort": "low"
            })
        
        # Trend-based recommendations
        if trend_analysis["status"] == "success":
            trends = trend_analysis["trends"]
            
            # Memory growth recommendations
            if "memory_count" in trends:
                growth_rate = trends["memory_count"]["growth_percentage"]
                if growth_rate > self.config["memory_growth_threshold"] * 100:
                    recommendations.append({
                        "category": "capacity_planning",
                        "priority": "medium",
                        "recommendation": f"Memory growing at {growth_rate:.1f}% per month. Plan for scaling.",
                        "impact_score": 0.7,
                        "implementation_effort": "medium"
                    })
            
            # Performance degradation recommendations
            if "api_performance" in trends:
                if trends["api_performance"]["trend_direction"] == "increasing":
                    recommendations.append({
                        "category": "performance",
                        "priority": "medium",
                        "recommendation": "API response time trending upward. Consider performance optimization.",
                        "impact_score": 0.6,
                        "implementation_effort": "medium"
                    })
        
        # General optimization recommendations
        recommendations.extend([
            {
                "category": "maintenance",
                "priority": "low",
                "recommendation": "Implement regular memory deduplication to reduce storage overhead.",
                "impact_score": 0.4,
                "implementation_effort": "low"
            },
            {
                "category": "monitoring",
                "priority": "medium",
                "recommendation": "Set up automated alerts for capacity thresholds.",
                "impact_score": 0.6,
                "implementation_effort": "low"
            },
            {
                "category": "backup",
                "priority": "medium",
                "recommendation": "Implement incremental backup strategy to reduce backup time.",
                "impact_score": 0.5,
                "implementation_effort": "medium"
            }
        ])
        
        # Store recommendations
        self._store_recommendations(recommendations)
        
        return recommendations
    
    def _store_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Store optimization recommendations"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.analysis_db) as conn:
            for rec in recommendations:
                conn.execute("""
                    INSERT INTO optimization_recommendations (
                        timestamp, category, priority, recommendation,
                        impact_score, implementation_effort
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    rec["category"],
                    rec["priority"],
                    rec["recommendation"],
                    rec["impact_score"],
                    rec["implementation_effort"]
                ))
    
    def generate_growth_charts(self) -> Dict[str, str]:
        """Generate visual charts for growth analysis"""
        self.logger.info("📊 Generating growth analysis charts...")
        
        chart_files = {}
        
        try:
            # Get data for charts
            with sqlite3.connect(self.analysis_db) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, memory_count, api_response_time_ms, 
                           system_cpu_percent, system_memory_percent
                    FROM memory_metrics 
                    WHERE timestamp >= datetime('now', '-30 days')
                    ORDER BY timestamp
                """)
                
                data = cursor.fetchall()
            
            if not data:
                return {"error": "No data available for charts"}
            
            timestamps = [datetime.fromisoformat(row[0]) for row in data]
            memory_counts = [row[1] for row in data if row[1] is not None]
            api_times = [row[2] for row in data if row[2] is not None]
            cpu_usage = [row[3] for row in data if row[3] is not None]
            memory_usage = [row[4] for row in data if row[4] is not None]
            
            # Memory count trend chart
            if memory_counts:
                plt.figure(figsize=(12, 6))
                plt.plot(timestamps[:len(memory_counts)], memory_counts, 'b-', linewidth=2)
                plt.title('Memory Count Trend (30 Days)', fontsize=14, fontweight='bold')
                plt.xlabel('Date')
                plt.ylabel('Memory Count')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                chart_file = self.reports_dir / "charts" / "memory_count_trend.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                chart_files["memory_trend"] = str(chart_file)
                plt.close()
            
            # API performance chart
            if api_times:
                plt.figure(figsize=(12, 6))
                plt.plot(timestamps[:len(api_times)], api_times, 'r-', linewidth=2)
                plt.title('API Response Time Trend (30 Days)', fontsize=14, fontweight='bold')
                plt.xlabel('Date')
                plt.ylabel('Response Time (ms)')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                chart_file = self.reports_dir / "charts" / "api_performance_trend.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                chart_files["api_trend"] = str(chart_file)
                plt.close()
            
            # System resources chart
            if cpu_usage and memory_usage:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
                
                ax1.plot(timestamps[:len(cpu_usage)], cpu_usage, 'g-', linewidth=2, label='CPU Usage')
                ax1.set_title('System Resource Usage (30 Days)', fontsize=14, fontweight='bold')
                ax1.set_ylabel('CPU Usage (%)')
                ax1.grid(True, alpha=0.3)
                ax1.legend()
                
                ax2.plot(timestamps[:len(memory_usage)], memory_usage, 'orange', linewidth=2, label='Memory Usage')
                ax2.set_xlabel('Date')
                ax2.set_ylabel('Memory Usage (%)')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                chart_file = self.reports_dir / "charts" / "system_resources_trend.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                chart_files["resources_trend"] = str(chart_file)
                plt.close()
            
        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
            chart_files["error"] = str(e)
        
        return chart_files
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive growth pattern analysis"""
        self.logger.info("🚀 Starting comprehensive growth pattern analysis...")
        
        analysis_start = time.time()
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "current_metrics": {},
            "trend_analysis": {},
            "capacity_projections": {},
            "optimization_recommendations": [],
            "charts": {},
            "summary": {}
        }
        
        try:
            # Step 1: Collect current metrics
            self.logger.info("📊 Collecting current metrics...")
            current_metrics = self.collect_current_metrics()
            self.store_metrics(current_metrics)
            results["current_metrics"] = current_metrics
            
            # Step 2: Analyze trends
            self.logger.info("📈 Analyzing growth trends...")
            trend_analysis = self.analyze_growth_trends(30)
            results["trend_analysis"] = trend_analysis
            
            # Step 3: Generate capacity projections
            self.logger.info("🔮 Generating capacity projections...")
            capacity_projections = self.generate_capacity_projections(90)
            results["capacity_projections"] = capacity_projections
            
            # Step 4: Generate optimization recommendations
            self.logger.info("💡 Generating optimization recommendations...")
            recommendations = self.generate_optimization_recommendations()
            results["optimization_recommendations"] = recommendations
            
            # Step 5: Generate visual charts
            self.logger.info("📊 Generating growth charts...")
            charts = self.generate_growth_charts()
            results["charts"] = charts
            
            # Step 6: Generate summary
            results["summary"] = self._generate_analysis_summary(results)
            
            results["analysis_duration_seconds"] = time.time() - analysis_start
            results["status"] = "success"
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            self.logger.error(f"Comprehensive analysis error: {e}")
        
        # Save results
        self._save_analysis_report(results)
        return results
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        summary = {
            "overall_health": "healthy",
            "critical_issues": [],
            "growth_insights": [],
            "optimization_priorities": [],
            "capacity_status": "adequate"
        }
        
        try:
            # Analyze current metrics
            current = results.get("current_metrics", {})
            if current.get("collection_errors"):
                summary["critical_issues"].append("Metrics collection issues detected")
                summary["overall_health"] = "warning"
            
            # Analyze trends
            trends = results.get("trend_analysis", {}).get("trends", {})
            if "memory_count" in trends:
                growth_rate = trends["memory_count"].get("growth_percentage", 0)
                if growth_rate > 20:
                    summary["growth_insights"].append(f"High memory growth rate: {growth_rate:.1f}% per month")
                    summary["capacity_status"] = "monitor"
            
            # Analyze recommendations
            recommendations = results.get("optimization_recommendations", [])
            high_priority = [r for r in recommendations if r.get("priority") == "high"]
            if high_priority:
                summary["critical_issues"].extend([r["recommendation"] for r in high_priority])
                summary["overall_health"] = "warning"
            
            # Top optimization priorities
            sorted_recs = sorted(recommendations, 
                               key=lambda x: (x.get("impact_score", 0), x.get("priority") == "high"), 
                               reverse=True)
            summary["optimization_priorities"] = [r["recommendation"] for r in sorted_recs[:3]]
            
            # Capacity projections analysis
            projections = results.get("capacity_projections", {}).get("projections", {})
            if "memory_count" in projections:
                projected = projections["memory_count"]["projected"]
                current_count = projections["memory_count"]["current"]
                if projected > current_count * 2:
                    summary["capacity_status"] = "plan_scaling"
                    summary["growth_insights"].append(f"Memory count projected to double in 90 days")
            
        except Exception as e:
            summary["critical_issues"].append(f"Summary generation error: {e}")
        
        return summary
    
    def _save_analysis_report(self, results: Dict[str, Any]):
        """Save comprehensive analysis report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"growth_analysis_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"📊 Analysis report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save analysis report: {e}")

def main():
    """Main growth pattern analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Memory System Growth Pattern Analyzer")
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive analysis')
    parser.add_argument('--metrics', action='store_true', help='Collect current metrics only')
    parser.add_argument('--trends', action='store_true', help='Analyze trends only')
    parser.add_argument('--projections', action='store_true', help='Generate capacity projections')
    parser.add_argument('--recommendations', action='store_true', help='Generate optimization recommendations')
    parser.add_argument('--charts', action='store_true', help='Generate growth charts')
    
    args = parser.parse_args()
    
    analyzer = GrowthPatternAnalyzer()
    
    if args.comprehensive:
        results = analyzer.run_comprehensive_analysis()
        print(f"✅ Comprehensive analysis completed. Status: {results['status']}")
        print(f"📊 Overall Health: {results['summary']['overall_health']}")
        print(f"⚠️  Critical Issues: {len(results['summary']['critical_issues'])}")
        print(f"💡 Optimization Recommendations: {len(results['optimization_recommendations'])}")
        return
    
    if args.metrics:
        metrics = analyzer.collect_current_metrics()
        analyzer.store_metrics(metrics)
        print(f"📊 Current metrics collected:")
        print(f"   Memory Count: {metrics['memory_count']}")
        print(f"   API Response: {metrics['api_response_time_ms']:.1f}ms")
        print(f"   System Load: CPU {metrics['system_cpu_percent']:.1f}%, RAM {metrics['system_memory_percent']:.1f}%")
        return
    
    if args.trends:
        trends = analyzer.analyze_growth_trends(30)
        print(f"📈 Trend analysis: {trends['status']}")
        if trends['status'] == 'success':
            for metric, data in trends['trends'].items():
                print(f"   {metric}: {data.get('trend_direction', 'unknown')}")
        return
    
    if args.projections:
        projections = analyzer.generate_capacity_projections(90)
        print(f"🔮 Capacity projections: {projections['status']}")
        if projections['status'] == 'success':
            for metric, data in projections['projections'].items():
                print(f"   {metric}: current {data.get('current', 0)} → projected {data.get('projected', 0)}")
        return
    
    if args.recommendations:
        recommendations = analyzer.generate_optimization_recommendations()
        print(f"💡 Generated {len(recommendations)} optimization recommendations:")
        for rec in recommendations[:5]:  # Show top 5
            print(f"   [{rec['priority']}] {rec['recommendation']}")
        return
    
    if args.charts:
        charts = analyzer.generate_growth_charts()
        print(f"📊 Generated charts: {', '.join(charts.keys())}")
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main() 