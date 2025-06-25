#!/usr/bin/env python3
"""
Advanced Memory System - Integrated Monitoring & Alerting
Combines real-time monitoring with intelligent alerting based on best practices
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import our monitoring and alerting components
from monitoring_dashboard import MemorySystemMonitor, SystemMetrics
from alert_system import AlertManager

class IntegratedMonitoringSystem:
    """Integrated monitoring and alerting system"""
    
    def __init__(self, monitor_config: str = "monitoring_config.json", 
                 alert_config: str = "alert_config.json"):
        self.monitor = MemorySystemMonitor(monitor_config)
        self.alert_manager = AlertManager(alert_config)
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integrated_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def start_integrated_monitoring(self):
        """Start integrated monitoring with real-time alerting"""
        self.running = True
        self.logger.info("🚀 Starting Integrated Memory System Monitor + Alerts")
        
        # Set baseline
        initial_metrics = self.monitor.collect_system_metrics()
        self.monitor.baseline_metrics = initial_metrics
        self.monitor.store_metrics(initial_metrics)
        
        self.logger.info(f"📋 Baseline established: {initial_metrics.memory_count} memories")
        
        while self.running:
            try:
                # Collect metrics
                metrics = self.monitor.collect_system_metrics()
                
                # Store metrics
                self.monitor.store_metrics(metrics)
                
                # Convert metrics to dict for alert evaluation
                metrics_dict = {
                    'memory_count': metrics.memory_count,
                    'api_response_time': metrics.api_response_time,
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'disk_usage': metrics.disk_usage,
                    'api_status': metrics.api_status,
                    'docker_containers': metrics.docker_containers,
                    'docker_images': metrics.docker_images
                }
                
                # Evaluate for alerts
                triggered_alerts = self.alert_manager.evaluate_metrics(metrics_dict)
                
                # Send any triggered alerts
                for alert in triggered_alerts:
                    self.alert_manager.send_alert(alert)
                    self.logger.warning(f"🚨 Alert triggered: {alert['rule_name']}")
                
                # Analyze baseline metrics for trends
                self.monitor.analyze_metrics(metrics)
                
                # Log current status
                status_emoji = "✅" if metrics.api_status == "UP" else "❌"
                alert_emoji = "🚨" if triggered_alerts else "📊"
                
                self.logger.info(f"{status_emoji} [{metrics.timestamp}] "
                               f"Memories: {metrics.memory_count}, "
                               f"API: {metrics.api_response_time:.2f}s, "
                               f"CPU: {metrics.cpu_usage:.1f}%, "
                               f"RAM: {metrics.memory_usage:.1f}% "
                               f"{alert_emoji}")
                
                # Wait for next collection
                await asyncio.sleep(self.monitor.config['monitoring_interval'])
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)  # Short wait before retry
        
        self.running = False
        self.logger.info("👋 Integrated monitoring stopped")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        monitor_report = self.monitor.generate_status_report()
        recent_alerts = self.alert_manager.get_recent_alerts(24)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": monitor_report,
            "alert_summary": {
                "total_alerts_24h": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a['level'] == 'CRITICAL']),
                "warning_alerts": len([a for a in recent_alerts if a['level'] == 'WARNING']),
                "recent_alerts": recent_alerts[:10]  # Last 10 alerts
            },
            "health_score": self._calculate_health_score(monitor_report, recent_alerts)
        }
    
    def _calculate_health_score(self, monitor_report: Dict[str, Any], 
                               recent_alerts: list) -> Dict[str, Any]:
        """Calculate system health score"""
        score = 100
        factors = []
        
        # Deduct points for recent alerts
        critical_count = len([a for a in recent_alerts if a['level'] == 'CRITICAL'])
        warning_count = len([a for a in recent_alerts if a['level'] == 'WARNING'])
        
        score -= critical_count * 20  # 20 points per critical alert
        score -= warning_count * 5    # 5 points per warning alert
        
        if critical_count > 0:
            factors.append(f"{critical_count} critical alerts")
        if warning_count > 0:
            factors.append(f"{warning_count} warning alerts")
        
        # Check API status
        latest_metrics = monitor_report.get('latest_metrics', {})
        if latest_metrics.get('api_status') == 'DOWN':
            score -= 30
            factors.append("API down")
        
        # Check response time
        avg_response_time = monitor_report.get('24h_summary', {}).get('avg_api_response_time', 0)
        if avg_response_time > 2.0:
            score -= 15
            factors.append("slow API response")
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        # Determine health level
        if score >= 90:
            level = "EXCELLENT"
        elif score >= 75:
            level = "GOOD"
        elif score >= 50:
            level = "FAIR"
        elif score >= 25:
            level = "POOR"
        else:
            level = "CRITICAL"
        
        return {
            "score": score,
            "level": level,
            "factors": factors
        }

def main():
    """Main integrated monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated Memory System Monitor + Alerts")
    parser.add_argument('--monitor-config', default='monitoring_config.json', 
                       help='Monitoring configuration file')
    parser.add_argument('--alert-config', default='alert_config.json', 
                       help='Alert configuration file')
    parser.add_argument('--report', action='store_true', 
                       help='Generate comprehensive report and exit')
    parser.add_argument('--test-alerts', action='store_true', 
                       help='Test alert system and exit')
    
    args = parser.parse_args()
    
    system = IntegratedMonitoringSystem(args.monitor_config, args.alert_config)
    
    if args.report:
        report = system.generate_comprehensive_report()
        print(json.dumps(report, indent=2))
        return
    
    if args.test_alerts:
        system.alert_manager.test_notifications()
        return
    
    # Start integrated monitoring
    try:
        asyncio.run(system.start_integrated_monitoring())
    except KeyboardInterrupt:
        print("\n👋 Integrated monitoring stopped")

if __name__ == "__main__":
    main() 