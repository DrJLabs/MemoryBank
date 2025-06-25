#!/usr/bin/env python3
"""
Advanced Memory System - Alert & Notification System
Based on automated monitoring best practices with threshold-based alerts and escalation
"""

import json
import smtplib
import subprocess
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    component: str
    metric: str
    threshold: float
    operator: str  # >, <, ==, !=
    severity: str  # INFO, WARNING, CRITICAL
    cooldown_minutes: int = 60
    notification_channels: List[str] = None

@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    name: str
    type: str  # email, webhook, desktop, log
    config: Dict[str, Any]
    enabled: bool = True

class AlertManager:
    """Advanced alert management system"""
    
    def __init__(self, config_file: str = "alert_config.json"):
        self.config = self._load_config(config_file)
        self.db_path = Path("monitoring.db")
        self.alert_rules = self._load_alert_rules()
        self.notification_channels = self._load_notification_channels()
        self.alert_history = {}
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load alert configuration"""
        default_config = {
            "smtp_server": "localhost",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "default_recipient": "admin@localhost",
            "webhook_endpoints": [],
            "escalation_timeout_minutes": 30,
            "alert_cooldown_minutes": 60
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
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules configuration"""
        default_rules = [
            {
                "name": "High API Response Time",
                "component": "api",
                "metric": "api_response_time",
                "threshold": 2.0,
                "operator": ">",
                "severity": "WARNING",
                "cooldown_minutes": 30,
                "notification_channels": ["email", "desktop"]
            },
            {
                "name": "API Down",
                "component": "api",
                "metric": "api_status",
                "threshold": "DOWN",
                "operator": "==",
                "severity": "CRITICAL",
                "cooldown_minutes": 5,
                "notification_channels": ["email", "webhook", "desktop"]
            },
            {
                "name": "High CPU Usage",
                "component": "system",
                "metric": "cpu_usage",
                "threshold": 80.0,
                "operator": ">",
                "severity": "WARNING",
                "cooldown_minutes": 60,
                "notification_channels": ["email"]
            },
            {
                "name": "High Memory Usage",
                "component": "system",
                "metric": "memory_usage",
                "threshold": 85.0,
                "operator": ">",
                "severity": "WARNING",
                "cooldown_minutes": 60,
                "notification_channels": ["email"]
            },
            {
                "name": "Critical Disk Usage",
                "component": "system",
                "metric": "disk_usage",
                "threshold": 90.0,
                "operator": ">",
                "severity": "CRITICAL",
                "cooldown_minutes": 30,
                "notification_channels": ["email", "webhook", "desktop"]
            },
            {
                "name": "Memory Growth Spike",
                "component": "memory_system",
                "metric": "memory_count_hourly_growth",
                "threshold": 50.0,
                "operator": ">",
                "severity": "WARNING",
                "cooldown_minutes": 120,
                "notification_channels": ["email"]
            }
        ]
        
        rules_file = Path("alert_rules.json")
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
        else:
            rules_data = default_rules
            with open(rules_file, 'w') as f:
                json.dump(rules_data, f, indent=2)
        
        return [AlertRule(**rule) for rule in rules_data]
    
    def _load_notification_channels(self) -> List[NotificationChannel]:
        """Load notification channels configuration"""
        default_channels = [
            {
                "name": "email",
                "type": "email",
                "config": {
                    "recipient": self.config.get("default_recipient", "admin@localhost"),
                    "subject_prefix": "[Memory-C* Alert]"
                },
                "enabled": True
            },
            {
                "name": "desktop",
                "type": "desktop",
                "config": {
                    "timeout": 5000
                },
                "enabled": True
            },
            {
                "name": "webhook",
                "type": "webhook",
                "config": {
                    "endpoints": self.config.get("webhook_endpoints", [])
                },
                "enabled": len(self.config.get("webhook_endpoints", [])) > 0
            },
            {
                "name": "log",
                "type": "log",
                "config": {
                    "log_file": "alerts.log"
                },
                "enabled": True
            }
        ]
        
        channels_file = Path("notification_channels.json")
        if channels_file.exists():
            with open(channels_file, 'r') as f:
                channels_data = json.load(f)
        else:
            channels_data = default_channels
            with open(channels_file, 'w') as f:
                json.dump(channels_data, f, indent=2)
        
        return [NotificationChannel(**channel) for channel in channels_data]
    
    def evaluate_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate metrics against alert rules and generate alerts"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if self._should_evaluate_rule(rule):
                alert = self._evaluate_rule(rule, metrics)
                if alert:
                    triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def _should_evaluate_rule(self, rule: AlertRule) -> bool:
        """Check if rule should be evaluated based on cooldown"""
        rule_key = f"{rule.component}_{rule.metric}"
        
        if rule_key in self.alert_history:
            last_alert_time = self.alert_history[rule_key]
            cooldown_period = timedelta(minutes=rule.cooldown_minutes)
            
            if datetime.now() - last_alert_time < cooldown_period:
                return False
        
        return True
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate a single rule against metrics"""
        metric_value = metrics.get(rule.metric)
        
        if metric_value is None:
            return None
        
        # Evaluate condition
        triggered = False
        if rule.operator == ">":
            triggered = float(metric_value) > rule.threshold
        elif rule.operator == "<":
            triggered = float(metric_value) < rule.threshold
        elif rule.operator == "==":
            triggered = str(metric_value) == str(rule.threshold)
        elif rule.operator == "!=":
            triggered = str(metric_value) != str(rule.threshold)
        
        if triggered:
            # Update alert history
            rule_key = f"{rule.component}_{rule.metric}"
            self.alert_history[rule_key] = datetime.now()
            
            return {
                "rule_name": rule.name,
                "component": rule.component,
                "metric": rule.metric,
                "value": metric_value,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "timestamp": datetime.now().isoformat(),
                "notification_channels": rule.notification_channels or ["log"]
            }
        
        return None
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send alert through configured notification channels"""
        channels_to_use = alert.get("notification_channels", ["log"])
        
        for channel_name in channels_to_use:
            channel = next((ch for ch in self.notification_channels if ch.name == channel_name), None)
            if channel and channel.enabled:
                try:
                    self._send_notification(channel, alert)
                except Exception as e:
                    print(f"❌ Failed to send alert via {channel_name}: {e}")
    
    def _send_notification(self, channel: NotificationChannel, alert: Dict[str, Any]):
        """Send notification through specific channel"""
        message = self._format_alert_message(alert)
        
        if channel.type == "email":
            self._send_email_notification(channel, alert, message)
        elif channel.type == "desktop":
            self._send_desktop_notification(channel, alert, message)
        elif channel.type == "webhook":
            self._send_webhook_notification(channel, alert, message)
        elif channel.type == "log":
            self._send_log_notification(channel, alert, message)
    
    def _format_alert_message(self, alert: Dict[str, Any]) -> str:
        """Format alert message"""
        severity_emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "CRITICAL": "🚨"
        }
        
        emoji = severity_emoji.get(alert["severity"], "📢")
        
        return f"""{emoji} Memory-C* Alert: {alert['rule_name']}

Component: {alert['component']}
Metric: {alert['metric']}
Current Value: {alert['value']}
Threshold: {alert['threshold']}
Severity: {alert['severity']}
Time: {alert['timestamp']}

This alert indicates that the {alert['component']} component has exceeded normal operating parameters.
Please investigate and take appropriate action if necessary."""
    
    def _send_email_notification(self, channel: NotificationChannel, alert: Dict[str, Any], message: str):
        """Send email notification"""
        if not self.config.get("smtp_server"):
            print("📧 Email notification skipped: SMTP not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get("smtp_username", "noreply@localhost")
            msg['To'] = channel.config["recipient"]
            msg['Subject'] = f"{channel.config['subject_prefix']} {alert['severity']}: {alert['rule_name']}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            if self.config.get("smtp_username"):
                server.starttls()
                server.login(self.config["smtp_username"], self.config["smtp_password"])
            
            text = msg.as_string()
            server.sendmail(msg['From'], msg['To'], text)
            server.quit()
            
            print(f"📧 Email alert sent to {channel.config['recipient']}")
        except Exception as e:
            print(f"❌ Email notification failed: {e}")
    
    def _send_desktop_notification(self, channel: NotificationChannel, alert: Dict[str, Any], message: str):
        """Send desktop notification"""
        try:
            # Try notify-send (Linux)
            subprocess.run([
                'notify-send',
                f"Memory-C* {alert['severity']}",
                f"{alert['rule_name']}: {alert['value']}",
                '-t', str(channel.config.get("timeout", 5000))
            ], check=False)
            print(f"🖥️ Desktop notification sent")
        except Exception as e:
            print(f"❌ Desktop notification failed: {e}")
    
    def _send_webhook_notification(self, channel: NotificationChannel, alert: Dict[str, Any], message: str):
        """Send webhook notification"""
        endpoints = channel.config.get("endpoints", [])
        
        for endpoint in endpoints:
            try:
                payload = {
                    "alert": alert,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(endpoint, json=payload, timeout=10)
                response.raise_for_status()
                print(f"🔗 Webhook alert sent to {endpoint}")
            except Exception as e:
                print(f"❌ Webhook notification to {endpoint} failed: {e}")
    
    def _send_log_notification(self, channel: NotificationChannel, alert: Dict[str, Any], message: str):
        """Send log notification"""
        log_file = Path(channel.config.get("log_file", "alerts.log"))
        
        try:
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {alert['severity']} - {alert['rule_name']}\n")
                f.write(f"Details: {json.dumps(alert, indent=2)}\n")
                f.write("-" * 80 + "\n")
            
            print(f"📝 Alert logged to {log_file}")
        except Exception as e:
            print(f"❌ Log notification failed: {e}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, level, component, message
                    FROM alerts 
                    WHERE timestamp > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                """.format(hours))
                
                return [dict(zip(['timestamp', 'level', 'component', 'message'], row)) 
                       for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Failed to get recent alerts: {e}")
            return []
    
    def test_notifications(self):
        """Test all notification channels"""
        test_alert = {
            "rule_name": "Test Alert",
            "component": "test",
            "metric": "test_metric",
            "value": "test_value",
            "threshold": "test_threshold",
            "severity": "INFO",
            "timestamp": datetime.now().isoformat(),
            "notification_channels": [ch.name for ch in self.notification_channels if ch.enabled]
        }
        
        print("🧪 Testing notification channels...")
        self.send_alert(test_alert)
        print("✅ Notification test completed")

def main():
    """Main alert system function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Memory System Alert Manager")
    parser.add_argument('--test', action='store_true', help='Test notification channels')
    parser.add_argument('--config', default='alert_config.json', help='Configuration file')
    parser.add_argument('--recent', type=int, default=24, help='Show alerts from recent hours')
    
    args = parser.parse_args()
    
    alert_manager = AlertManager(args.config)
    
    if args.test:
        alert_manager.test_notifications()
        return
    
    if args.recent:
        alerts = alert_manager.get_recent_alerts(args.recent)
        if alerts:
            print(f"📋 Recent alerts ({args.recent}h):")
            for alert in alerts:
                print(f"  {alert['timestamp']} [{alert['level']}] {alert['component']}: {alert['message']}")
        else:
            print(f"✅ No alerts in the last {args.recent} hours")

if __name__ == "__main__":
    main() 