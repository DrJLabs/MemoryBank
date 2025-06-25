#!/usr/bin/env python3
"""
FIXED Growth Pattern Analyzer for OpenMemory System
Addresses API connectivity issues identified in Phase 4
"""

import json
import sqlite3
import time
import requests
import subprocess
import sys
from datetime import datetime

class FixedGrowthAnalyzer:
    def __init__(self, db_path: str = "growth_analysis_fixed.db"):
        self.db_path = db_path
        self.api_base = "http://localhost:8765"
        self.qdrant_base = "http://localhost:6333"
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_api_connectivity(self):
        """Test API connectivity and get memory statistics"""
        print("🔍 Testing API Connectivity...")
        
        results = {
            'overall_status': 'UNKNOWN',
            'total_memories': 0,
            'active_apps': 0,
            'qdrant_points': 0,
            'endpoints': {}
        }
        
        # Test apps endpoint (primary source of memory data)
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base}/api/v1/apps/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                apps_data = response.json()
                results['total_memories'] = sum(app.get('total_memories_created', 0) 
                                              for app in apps_data.get('apps', []))
                results['active_apps'] = len([app for app in apps_data.get('apps', []) 
                                             if app.get('is_active', False)])
                results['endpoints']['/api/v1/apps/'] = {
                    'status_code': 200,
                    'response_time': response_time,
                    'success': True
                }
                results['overall_status'] = 'HEALTHY'
                results['apps_data'] = apps_data
            else:
                results['endpoints']['/api/v1/apps/'] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': False
                }
                results['overall_status'] = 'FAILED'
                
        except Exception as e:
            results['endpoints']['/api/v1/apps/'] = {
                'error': str(e),
                'success': False
            }
            results['overall_status'] = 'FAILED'
        
        # Test Qdrant connectivity
        try:
            qdrant_response = self.session.get(f"{self.qdrant_base}/collections/openmemory")
            if qdrant_response.status_code == 200:
                coll_data = qdrant_response.json()
                results['qdrant_points'] = coll_data.get('result', {}).get('points_count', 0)
        except:
            pass
        
        return results
    
    def collect_system_metrics(self):
        """Collect basic system metrics"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            # Fallback using basic commands
            try:
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
                    'cpu_percent': 0.0,  # Not easily available without psutil
                    'memory_percent': memory_percent,
                    'timestamp': datetime.now().isoformat()
                }
            except:
                return {
                    'cpu_percent': 0.0,
                    'memory_percent': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
    
    def run_complete_analysis(self):
        """Run complete connectivity analysis"""
        print("🚀 Starting Fixed Growth Pattern Analysis...")
        print("=" * 60)
        
        # Test API connectivity
        api_results = self.test_api_connectivity()
        system_metrics = self.collect_system_metrics()
        
        # Generate report
        print("\n🔌 API CONNECTIVITY STATUS")
        print("-" * 40)
        
        apps_endpoint = api_results['endpoints'].get('/api/v1/apps/', {})
        if apps_endpoint.get('success'):
            print(f"✅ /api/v1/apps/        WORKING    ({apps_endpoint.get('response_time', 0):.3f}s)")
        else:
            print(f"❌ /api/v1/apps/        FAILED     {apps_endpoint.get('error', 'Unknown error')}")
        
        print("\n💾 MEMORY SYSTEM STATUS")
        print("-" * 40)
        print(f"Total Memories:     {api_results['total_memories']:,}")
        print(f"Active Apps:        {api_results['active_apps']}")
        print(f"Qdrant Points:      {api_results['qdrant_points']:,}")
        print(f"Overall Status:     {api_results['overall_status']}")
        
        print("\n🖥️  SYSTEM RESOURCES")
        print("-" * 40)
        print(f"CPU Usage:          {system_metrics['cpu_percent']:.1f}%")
        print(f"Memory Usage:       {system_metrics['memory_percent']:.1f}%")
        
        # Show app details if available
        if 'apps_data' in api_results:
            print("\n📱 APPLICATION DETAILS")
            print("-" * 40)
            for app in api_results['apps_data'].get('apps', []):
                status_icon = "🟢" if app.get('is_active') else "🔴"
                print(f"{status_icon} {app.get('name', 'Unknown'):15} "
                      f"Memories: {app.get('total_memories_created', 0):,}")
        
        print("\n" + "=" * 60)
        print(f"✅ Analysis completed - Status: {api_results['overall_status']}")
        
        return api_results

def main():
    analyzer = FixedGrowthAnalyzer()
    try:
        results = analyzer.run_complete_analysis()
        if results['overall_status'] == 'HEALTHY':
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"💥 Analysis failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
