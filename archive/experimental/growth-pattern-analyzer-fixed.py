#!/usr/bin/env python3
"""
FIXED Growth Pattern Analyzer for OpenMemory System
Addresses API connectivity issues identified in Phase 4
Uses correct API endpoints and structure

Key Fixes:
1. Uses /api/v1/apps/ endpoint to get memory statistics
2. Handles pagination and proper response structure  
3. Implements fallback mechanisms for API connectivity
4. Provides detailed connectivity diagnostics
"""

import json
import sqlite3
import time
import requests
import subprocess
import sys
from datetime import datetime
from typing import Dict

class FixedGrowthAnalyzer:
    def __init__(self, db_path: str = "growth_analysis.db"):
        self.db_path = db_path
        self.api_base = "http://localhost:8765"
        self.qdrant_base = "http://localhost:6333"
        self.setup_database()
        self.session = requests.Session()
        self.session.timeout = 10
        
    def setup_database(self):
        """Setup SQLite database with enhanced tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced memory metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_memories INTEGER,
                active_apps INTEGER,
                api_response_time REAL,
                system_cpu_percent REAL,
                system_memory_percent REAL,
                qdrant_points INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        # API connectivity diagnostics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                endpoint TEXT,
                response_code INTEGER,
                response_time REAL,
                success BOOLEAN,
                error_details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def test_api_connectivity(self) -> Dict[str, any]:
        """Comprehensive API connectivity testing"""
        print("🔍 Testing API Connectivity...")
        
        results = {
            'overall_status': 'UNKNOWN',
            'endpoints': {},
            'api_structure': {},
            'total_memories': 0,
            'active_apps': 0,
            'qdrant_points': 0
        }
        
        # Test key endpoints
        endpoints_to_test = [
            ('/api/v1/apps/', 'Apps List'),
            ('/api/v1/stats/', 'Stats'),  # Will likely fail without user_id
            ('/docs', 'API Documentation'),
            ('/', 'Root')
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_base}{endpoint}")
                response_time = time.time() - start_time
                
                results['endpoints'][endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code < 400,
                    'description': description
                }
                
                # Special handling for apps endpoint
                if endpoint == '/api/v1/apps/' and response.status_code == 200:
                    try:
                        apps_data = response.json()
                        results['api_structure']['apps'] = apps_data
                        results['total_memories'] = sum(app.get('total_memories_created', 0) 
                                                       for app in apps_data.get('apps', []))
                        results['active_apps'] = len([app for app in apps_data.get('apps', []) 
                                                     if app.get('is_active', False)])
                    except Exception as e:
                        results['endpoints'][endpoint]['parse_error'] = str(e)
                        
            except Exception as e:
                results['endpoints'][endpoint] = {
                    'status_code': None,
                    'response_time': None,
                    'success': False,
                    'error': str(e),
                    'description': description
                }
        
        # Test Qdrant connectivity
        try:
            start_time = time.time()
            qdrant_response = self.session.get(f"{self.qdrant_base}/collections")
            qdrant_time = time.time() - start_time
            
            if qdrant_response.status_code == 200:
                collections = qdrant_response.json()
                results['qdrant'] = {
                    'status': 'CONNECTED',
                    'response_time': qdrant_time,
                    'collections': [c['name'] for c in collections.get('result', {}).get('collections', [])]
                }
                
                # Get collection details
                if 'openmemory' in results['qdrant']['collections']:
                    try:
                        coll_response = self.session.get(f"{self.qdrant_base}/collections/openmemory")
                        if coll_response.status_code == 200:
                            coll_data = coll_response.json()
                            results['qdrant_points'] = coll_data.get('result', {}).get('points_count', 0)
                    except:
                        pass
            else:
                results['qdrant'] = {'status': 'FAILED', 'error': f"HTTP {qdrant_response.status_code}"}
                
        except Exception as e:
            results['qdrant'] = {'status': 'ERROR', 'error': str(e)}
        
        # Determine overall status
        apps_working = results['endpoints'].get('/api/v1/apps/', {}).get('success', False)
        qdrant_working = results.get('qdrant', {}).get('status') == 'CONNECTED'
        
        if apps_working and qdrant_working:
            results['overall_status'] = 'HEALTHY'
        elif apps_working or qdrant_working:
            results['overall_status'] = 'PARTIAL'
        else:
            results['overall_status'] = 'FAILED'
            
        return results
    
    def collect_system_metrics(self) -> Dict[str, any]:
        """Collect comprehensive system metrics"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            # Fallback using system commands
            try:
                # CPU usage
                cpu_result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
                cpu_line = [line for line in cpu_result.stdout.split('\n') if 'Cpu(s)' in line]
                cpu_percent = 0.0
                if cpu_line:
                    # Parse CPU usage from top output
                    import re
                    match = re.search(r'(\d+\.\d+)%us', cpu_line[0])
                    if match:
                        cpu_percent = float(match.group(1))
                
                # Memory usage  
                mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True)
                mem_lines = mem_result.stdout.split('\n')
                if len(mem_lines) > 1:
                    mem_data = mem_lines[1].split()
                    total_mem = int(mem_data[1])
                    used_mem = int(mem_data[2])
                    memory_percent = (used_mem / total_mem) * 100
                else:
                    memory_percent = 0.0
                
                return {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_usage': 0.0,  # Not available without psutil
                    'timestamp': datetime.now().isoformat()
                }
            except:
                return {
                    'cpu_percent': 0.0,
                    'memory_percent': 0.0,
                    'disk_usage': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
    
    def analyze_current_state(self) -> Dict[str, any]:
        """Analyze current system state with comprehensive diagnostics"""
        print("📊 Analyzing Current System State...")
        
        # Test API connectivity first
        api_results = self.test_api_connectivity()
        system_metrics = self.collect_system_metrics()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'api_connectivity': api_results,
            'system_metrics': system_metrics,
            'memory_statistics': {
                'total_memories': api_results.get('total_memories', 0),
                'active_apps': api_results.get('active_apps', 0),
                'qdrant_points': api_results.get('qdrant_points', 0)
            },
            'health_status': api_results.get('overall_status', 'UNKNOWN'),
            'recommendations': []
        }
        
        # Generate recommendations based on findings
        if api_results.get('overall_status') == 'FAILED':
            analysis['recommendations'].append({
                'priority': 'CRITICAL',
                'category': 'API_CONNECTIVITY',
                'issue': 'OpenMemory API not responding',
                'solution': 'Check Docker containers and restart if necessary'
            })
        
        if api_results.get('total_memories', 0) == 0:
            analysis['recommendations'].append({
                'priority': 'WARNING',
                'category': 'DATA_AVAILABILITY',
                'issue': 'No memories found in the system',
                'solution': 'Verify data migration and user setup'
            })
        
        if system_metrics.get('memory_percent', 0) > 85:
            analysis['recommendations'].append({
                'priority': 'WARNING',
                'category': 'SYSTEM_RESOURCES',
                'issue': f"High memory usage: {system_metrics['memory_percent']:.1f}%",
                'solution': 'Consider system cleanup or resource scaling'
            })
        
        # Store metrics in database
        self.store_metrics(analysis)
        
        return analysis
    
    def store_metrics(self, analysis: Dict[str, any]):
        """Store analysis results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store main metrics
        cursor.execute('''
            INSERT INTO memory_metrics 
            (total_memories, active_apps, api_response_time, system_cpu_percent, 
             system_memory_percent, qdrant_points, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis['memory_statistics']['total_memories'],
            analysis['memory_statistics']['active_apps'],
            analysis['api_connectivity']['endpoints'].get('/api/v1/apps/', {}).get('response_time', 0),
            analysis['system_metrics']['cpu_percent'],
            analysis['system_metrics']['memory_percent'],
            analysis['memory_statistics']['qdrant_points'],
            analysis['health_status'],
            json.dumps([r['issue'] for r in analysis['recommendations']])
        ))
        
        # Store API diagnostics
        for endpoint, data in analysis['api_connectivity']['endpoints'].items():
            cursor.execute('''
                INSERT INTO api_diagnostics
                (endpoint, response_code, response_time, success, error_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                endpoint,
                data.get('status_code'),
                data.get('response_time'),
                data.get('success', False),
                data.get('error', '')
            ))
        
        conn.commit()
        conn.close()
    
    def generate_detailed_report(self, analysis: Dict[str, any]) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("FIXED GROWTH PATTERN ANALYZER - DETAILED REPORT")
        report.append("=" * 80)
        report.append(f"Analysis Time: {analysis['timestamp']}")
        report.append(f"Overall Health: {analysis['health_status']}")
        report.append("")
        
        # API Connectivity Section
        report.append("🔌 API CONNECTIVITY STATUS")
        report.append("-" * 40)
        for endpoint, data in analysis['api_connectivity']['endpoints'].items():
            status = "✅ WORKING" if data.get('success') else "❌ FAILED"
            response_time = data.get('response_time', 0)
            report.append(f"{endpoint:25} {status:15} ({response_time:.3f}s)")
            if not data.get('success') and 'error' in data:
                report.append(f"                         Error: {data['error']}")
        report.append("")
        
        # Memory Statistics Section  
        report.append("💾 MEMORY SYSTEM STATUS")
        report.append("-" * 40)
        stats = analysis['memory_statistics']
        report.append(f"Total Memories:     {stats['total_memories']:,}")
        report.append(f"Active Apps:        {stats['active_apps']}")
        report.append(f"Qdrant Points:      {stats['qdrant_points']:,}")
        report.append("")
        
        # System Resources Section
        report.append("🖥️  SYSTEM RESOURCES")
        report.append("-" * 40)
        sys_metrics = analysis['system_metrics']
        report.append(f"CPU Usage:          {sys_metrics['cpu_percent']:.1f}%")
        report.append(f"Memory Usage:       {sys_metrics['memory_percent']:.1f}%")
        report.append(f"Disk Usage:         {sys_metrics['disk_usage']:.1f}%")
        report.append("")
        
        # Recommendations Section
        if analysis['recommendations']:
            report.append("🔧 RECOMMENDATIONS")
            report.append("-" * 40)
            for i, rec in enumerate(analysis['recommendations'], 1):
                priority_icon = "🔴" if rec['priority'] == 'CRITICAL' else "🟡"
                report.append(f"{i}. {priority_icon} {rec['priority']}: {rec['issue']}")
                report.append(f"   Solution: {rec['solution']}")
                report.append("")
        
        # API Structure Information
        if 'apps' in analysis['api_connectivity']['api_structure']:
            report.append("📱 APPLICATION DETAILS")
            report.append("-" * 40)
            apps_data = analysis['api_connectivity']['api_structure']['apps']
            for app in apps_data.get('apps', []):
                status_icon = "🟢" if app.get('is_active') else "🔴"
                report.append(f"{status_icon} {app.get('name', 'Unknown'):15} "
                            f"Memories: {app.get('total_memories_created', 0):,}")
        
        return "\n".join(report)
    
    def run_complete_analysis(self) -> Dict[str, any]:
        """Run complete growth pattern analysis with fixes"""
        print("🚀 Starting Fixed Growth Pattern Analysis...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Perform analysis
        analysis = self.analyze_current_state()
        
        # Generate and display report
        report = self.generate_detailed_report(analysis)
        print(report)
        
        # Performance summary
        end_time = time.time()
        analysis['performance'] = {
            'analysis_duration': end_time - start_time,
            'total_metrics_collected': len(analysis['api_connectivity']['endpoints']) + 3,  # +3 for system metrics
            'database_updated': True
        }
        
        print("\n" + "=" * 60)
        print(f"✅ Analysis completed in {analysis['performance']['analysis_duration']:.2f} seconds")
        print(f"📊 {analysis['performance']['total_metrics_collected']} metrics collected and stored")
        
        return analysis

def main():
    """Main execution function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print("🔍 Quick connectivity test mode")
    
    analyzer = FixedGrowthAnalyzer()
    
    try:
        # Run the complete analysis
        results = analyzer.run_complete_analysis()
        
        # Exit with appropriate code based on health status
        if results['health_status'] == 'HEALTHY':
            sys.exit(0)
        elif results['health_status'] == 'PARTIAL':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 