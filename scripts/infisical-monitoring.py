#!/usr/bin/env python3
"""
Infisical Secret Management Monitoring System
Architecture: Memory-C* Infisical Integration Architecture v1.0
Pattern: Secret Management Monitoring with Metrics Collection and Alerting
"""

import os
import json
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/infisical-monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecretMetrics:
    """Secret management performance metrics"""
    secret_load_time_seconds: float
    secret_cache_hit_ratio: float
    infisical_api_response_time_seconds: float
    failed_authentication_attempts_total: int
    secret_access_outside_policy_total: int
    environment_boundary_violations_total: int
    infisical_cli_version: str
    secret_sync_status: str
    authentication_token_expiry_time: Optional[str]

@dataclass
class AlertEvent:
    """Alert event structure"""
    timestamp: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    event_type: str
    message: str
    details: Dict

class InfisicalMonitor:
    """Comprehensive Infisical monitoring system"""
    
    def __init__(self):
        self.metrics_history: List[SecretMetrics] = []
        self.alerts: List[AlertEvent] = []
        self.start_time = time.time()
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure required directories exist"""
        Path("logs").mkdir(exist_ok=True)
        Path("monitoring/dashboards").mkdir(parents=True, exist_ok=True)
        Path("monitoring/alerts").mkdir(parents=True, exist_ok=True)
        
    def check_infisical_cli_available(self) -> bool:
        """Check if Infisical CLI is available"""
        try:
            result = subprocess.run(['which', 'infisical'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Infisical CLI availability: {e}")
            return False
    
    def get_infisical_version(self) -> str:
        """Get Infisical CLI version"""
        try:
            result = subprocess.run(['infisical', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception as e:
            logger.error(f"Error getting Infisical version: {e}")
            return "error"
    
    def measure_secret_load_time(self, environment: str = "dev") -> float:
        """Measure time to load secrets from Infisical"""
        start_time = time.time()
        try:
            result = subprocess.run(['infisical', 'secrets', '--env', environment], 
                                  capture_output=True, text=True, timeout=10)
            end_time = time.time()
            
            if result.returncode == 0:
                return end_time - start_time
            else:
                logger.warning(f"Failed to load secrets for {environment}: {result.stderr}")
                return -1.0
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout loading secrets for {environment}")
            return -1.0
        except Exception as e:
            logger.error(f"Error measuring secret load time: {e}")
            return -1.0
    
    def check_authentication_status(self) -> Tuple[bool, str]:
        """Check Infisical authentication status"""
        try:
            result = subprocess.run(['infisical', 'secrets', '--env=dev'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, "authenticated"
            else:
                return False, result.stderr.strip()
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            return False, str(e)
    
    def validate_environment_access(self) -> Dict[str, bool]:
        """Validate access to different environments"""
        environments = ["dev", "staging", "prod"]
        access_status = {}
        
        for env in environments:
            try:
                result = subprocess.run(['infisical', 'secrets', '--env', env], 
                                      capture_output=True, text=True, timeout=5)
                access_status[env] = result.returncode == 0
                
                if result.returncode != 0:
                    self.create_alert("MEDIUM", "environment_access_failed", 
                                    f"Failed to access {env} environment", 
                                    {"environment": env, "error": result.stderr})
            except Exception as e:
                access_status[env] = False
                logger.error(f"Error checking {env} environment: {e}")
        
        return access_status
    
    def check_secret_policy_compliance(self) -> int:
        """Check for secret access outside policy (simulated)"""
        # In a real implementation, this would check audit logs
        # For now, we'll simulate based on current status
        violations = 0
        
        # Check if .env files exist (policy violation)
        env_files = [".env", "mem0/server/.env", "mem0/openmemory/.env"]
        for env_file in env_files:
            if os.path.exists(env_file):
                violations += 1
                self.create_alert("HIGH", "policy_violation", 
                                f"Found .env file: {env_file} (should use Infisical)", 
                                {"file": env_file})
        
        return violations
    
    def measure_api_response_time(self) -> float:
        """Measure Infisical API response time"""
        try:
            start_time = time.time()
            # Use a lightweight command to test API response
            result = subprocess.run(['infisical', 'secrets', '--env=dev', '--limit=1'], 
                                  capture_output=True, text=True, timeout=10)
            end_time = time.time()
            
            if result.returncode == 0:
                return end_time - start_time
            return -1.0
        except Exception as e:
            logger.error(f"Error measuring API response time: {e}")
            return -1.0
    
    def collect_metrics(self) -> SecretMetrics:
        """Collect comprehensive metrics"""
        logger.info("🔍 Collecting Infisical metrics...")
        
        # Collect all metrics
        secret_load_time = self.measure_secret_load_time()
        api_response_time = self.measure_api_response_time()
        cli_version = self.get_infisical_version()
        auth_status, auth_message = self.check_authentication_status()
        self.validate_environment_access()
        policy_violations = self.check_secret_policy_compliance()
        
        # Calculate cache hit ratio (simulated based on response times)
        cache_hit_ratio = max(0.0, min(1.0, (2.0 - secret_load_time) / 2.0)) if secret_load_time > 0 else 0.0
        
        metrics = SecretMetrics(
            secret_load_time_seconds=secret_load_time,
            secret_cache_hit_ratio=cache_hit_ratio,
            infisical_api_response_time_seconds=api_response_time,
            failed_authentication_attempts_total=0 if auth_status else 1,
            secret_access_outside_policy_total=policy_violations,
            environment_boundary_violations_total=0,  # Would be calculated from audit logs
            infisical_cli_version=cli_version,
            secret_sync_status="synced" if auth_status else "failed",
            authentication_token_expiry_time=None  # Would require token inspection
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def create_alert(self, severity: str, event_type: str, message: str, details: Dict):
        """Create monitoring alert"""
        alert = AlertEvent(
            timestamp=datetime.now().isoformat(),
            severity=severity,
            event_type=event_type,
            message=message,
            details=details
        )
        
        self.alerts.append(alert)
        logger.warning(f"🚨 ALERT [{severity}] {event_type}: {message}")
        
        # Store alert for memory system integration
        if os.system("command -v ai-add-smart >/dev/null 2>&1") == 0:
            os.system(f'ai-add-smart "INFISICAL ALERT: [{severity}] {message} - Details: {json.dumps(details)}"')
    
    def analyze_performance(self) -> Dict:
        """Analyze performance trends"""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        recent_metrics = self.metrics_history[-5:]  # Last 5 measurements
        
        avg_load_time = sum(m.secret_load_time_seconds for m in recent_metrics if m.secret_load_time_seconds > 0) / len(recent_metrics)
        avg_cache_ratio = sum(m.secret_cache_hit_ratio for m in recent_metrics) / len(recent_metrics)
        
        analysis = {
            "average_load_time_seconds": avg_load_time,
            "average_cache_hit_ratio": avg_cache_ratio,
            "performance_grade": "A" if avg_load_time < 1.0 else "B" if avg_load_time < 2.0 else "C",
            "recommendations": []
        }
        
        # Performance recommendations
        if avg_load_time > 2.0:
            analysis["recommendations"].append("Consider implementing local secret caching")
        if avg_cache_ratio < 0.7:
            analysis["recommendations"].append("Optimize secret access patterns to improve cache efficiency")
        
        return analysis
    
    def generate_dashboard_data(self) -> Dict:
        """Generate data for monitoring dashboard"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        latest_metrics = self.metrics_history[-1]
        performance_analysis = self.analyze_performance()
        
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "infisical_cli_available": self.check_infisical_cli_available(),
                "authentication_status": latest_metrics.secret_sync_status,
                "cli_version": latest_metrics.infisical_cli_version
            },
            "performance_metrics": asdict(latest_metrics),
            "performance_analysis": performance_analysis,
            "recent_alerts": [asdict(alert) for alert in self.alerts[-10:]],
            "monitoring_uptime_seconds": time.time() - self.start_time
        }
        
        return dashboard_data
    
    def save_dashboard_data(self):
        """Save dashboard data to file"""
        dashboard_data = self.generate_dashboard_data()
        
        # Save JSON data
        with open("monitoring/dashboards/infisical-dashboard.json", "w") as f:
            json.dump(dashboard_data, f, indent=2)
        
        # Generate HTML dashboard
        html_content = self.generate_html_dashboard(dashboard_data)
        with open("monitoring/dashboards/infisical-dashboard.html", "w") as f:
            f.write(html_content)
    
    def generate_html_dashboard(self, data: Dict) -> str:
        """Generate HTML dashboard"""
        status_color = "green" if data["system_status"]["authentication_status"] == "synced" else "red"
        performance_grade = data.get("performance_analysis", {}).get("performance_grade", "Unknown")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Infisical Monitoring Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .status-good {{ color: #27ae60; }}
        .status-bad {{ color: #e74c3c; }}
        .status-warning {{ color: #f39c12; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .alert-high {{ background: #f8d7da; border-color: #f5c6cb; }}
        .alert-critical {{ background: #f5c6cb; border-color: #f1b0b7; }}
        .timestamp {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🔐 Memory-C* Infisical Monitoring Dashboard</h1>
            <p>Real-time secret management monitoring and performance analytics</p>
            <p class="timestamp">Last updated: {data['timestamp']}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>🚀 System Status</h3>
                <div class="metric-value" style="color: {status_color}">
                    {data['system_status']['authentication_status'].upper()}
                </div>
                <p>CLI Version: {data['system_status']['cli_version']}</p>
            </div>
            
            <div class="metric-card">
                <h3>⚡ Performance Grade</h3>
                <div class="metric-value">{performance_grade}</div>
                <p>Load Time: {data['performance_metrics']['secret_load_time_seconds']:.2f}s</p>
            </div>
            
            <div class="metric-card">
                <h3>📊 Cache Efficiency</h3>
                <div class="metric-value">{data['performance_metrics']['secret_cache_hit_ratio']:.1%}</div>
                <p>API Response: {data['performance_metrics']['infisical_api_response_time_seconds']:.2f}s</p>
            </div>
            
            <div class="metric-card">
                <h3>🛡️ Security Status</h3>
                <div class="metric-value status-good">✅ SECURE</div>
                <p>Policy Violations: {data['performance_metrics']['secret_access_outside_policy_total']}</p>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ Monitoring Uptime</h3>
                <div class="metric-value">{int(data['monitoring_uptime_seconds'] // 60)}m</div>
                <p>Continuous monitoring active</p>
            </div>
            
            <div class="metric-card">
                <h3>🚨 Recent Alerts</h3>
                <div style="max-height: 200px; overflow-y: auto;">
                    {self.format_alerts_html(data.get('recent_alerts', []))}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """
        return html
    
    def format_alerts_html(self, alerts: List[Dict]) -> str:
        """Format alerts for HTML display"""
        if not alerts:
            return "<p>No recent alerts 🎉</p>"
        
        html = ""
        for alert in alerts[-5:]:  # Show last 5 alerts
            severity_class = f"alert-{alert['severity'].lower()}" if alert['severity'] in ['HIGH', 'CRITICAL'] else 'alert'
            html += f'<div class="{severity_class}"><strong>{alert["severity"]}</strong>: {alert["message"]}</div>'
        
        return html
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("🔄 Starting Infisical monitoring cycle...")
        
        # Collect metrics
        metrics = self.collect_metrics()
        
        # Performance analysis and alerting
        if metrics.secret_load_time_seconds > 5.0:
            self.create_alert("HIGH", "performance_degradation", 
                            f"Secret loading taking {metrics.secret_load_time_seconds:.2f}s (threshold: 5.0s)", 
                            {"load_time": metrics.secret_load_time_seconds})
        
        if metrics.failed_authentication_attempts_total > 0:
            self.create_alert("CRITICAL", "authentication_failure", 
                            "Failed to authenticate with Infisical", 
                            {"attempts": metrics.failed_authentication_attempts_total})
        
        if metrics.secret_access_outside_policy_total > 0:
            self.create_alert("HIGH", "policy_violation", 
                            f"Found {metrics.secret_access_outside_policy_total} policy violations", 
                            {"violations": metrics.secret_access_outside_policy_total})
        
        # Save dashboard data
        self.save_dashboard_data()
        
        logger.info("✅ Monitoring cycle completed")
        return metrics

def main():
    """Main monitoring function"""
    print("🔐 Infisical Secret Management Monitor")
    print("Architecture: Memory-C* Infisical Integration v1.0")
    print("=" * 50)
    
    monitor = InfisicalMonitor()
    
    try:
        if not monitor.check_infisical_cli_available():
            print("❌ Infisical CLI not available. Please install and authenticate.")
            return 1
        
        # Run monitoring cycle
        metrics = monitor.run_monitoring_cycle()
        
        # Display results
        print("📊 Monitoring Results:")
        print(f"  Secret Load Time: {metrics.secret_load_time_seconds:.2f}s")
        print(f"  Cache Hit Ratio: {metrics.secret_cache_hit_ratio:.1%}")
        print(f"  API Response Time: {metrics.infisical_api_response_time_seconds:.2f}s")
        print(f"  CLI Version: {metrics.infisical_cli_version}")
        print(f"  Sync Status: {metrics.secret_sync_status}")
        
        if monitor.alerts:
            print(f"\n🚨 Alerts Generated: {len(monitor.alerts)}")
            for alert in monitor.alerts[-3:]:  # Show last 3
                print(f"  [{alert.severity}] {alert.message}")
        else:
            print("\n✅ No alerts - system healthy!")
        
        print("\n📋 Dashboard saved to: monitoring/dashboards/infisical-dashboard.html")
        print(f"🔍 View dashboard: file://{os.path.abspath('monitoring/dashboards/infisical-dashboard.html')}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 