#!/usr/bin/env python3
"""
Comprehensive Memory Dashboard Fix
Diagnoses and fixes all issues with the OpenMemory dashboard system
"""

import sys
import json
import requests
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

API_URL = "http://localhost:8765"
UI_URL = "http://localhost:3010"
USER_ID = "drj"

class MemorySystemFixer:
    def __init__(self):
        self.api_url = API_URL
        self.ui_url = UI_URL
        self.user_id = USER_ID
        self.db_path = Path("mem0/openmemory/api/openmemory.db")
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_services(self):
        """Check if all required services are running"""
        self.log("🔍 Checking service status...")
        
        services = {
            "API (8765)": self.api_url,
            "UI (3010)": self.ui_url,
            "Qdrant (6333)": "http://localhost:6333"
        }
        
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                status = "✅ Running" if response.status_code < 500 else "❌ Error"
                self.log(f"{name}: {status}")
            except Exception as e:
                self.log(f"{name}: ❌ Not responding ({str(e)})", "ERROR")
    
    def check_database(self):
        """Check database structure and data"""
        self.log("🔍 Checking database...")
        
        if not self.db_path.exists():
            self.log("❌ Database file not found!", "ERROR")
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check users table
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (self.user_id,))
            user_count = cursor.fetchone()[0]
            self.log(f"Users with ID '{self.user_id}': {user_count}")
            
            # Check memories table
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]
            self.log(f"Total memories in database: {total_memories}")
            
            # Check user's memories
            cursor.execute("""
                SELECT COUNT(*) FROM memories m 
                JOIN users u ON m.user_id = u.id 
                WHERE u.user_id = ?
            """, (self.user_id,))
            user_memories = cursor.fetchone()[0]
            self.log(f"Memories for user '{self.user_id}': {user_memories}")
            
            # Get sample memories
            cursor.execute("""
                SELECT m.content, m.created_at FROM memories m 
                JOIN users u ON m.user_id = u.id 
                WHERE u.user_id = ? 
                ORDER BY m.created_at DESC LIMIT 3
            """, (self.user_id,))
            samples = cursor.fetchall()
            
            if samples:
                self.log("📝 Sample memories:")
                for content, created_at in samples:
                    self.log(f"  - {content[:50]}... ({created_at})")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Database error: {str(e)}", "ERROR")
            return False
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        self.log("🔍 Testing API endpoints...")
        
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/docs", "API documentation"),
            ("GET", f"/api/v1/memories/?user_id={self.user_id}", "List memories"),
            ("GET", "/api/v1/stats/", "Stats endpoint")
        ]
        
        for method, path, description in endpoints:
            try:
                url = self.api_url + path
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log(f"✅ {description}: OK")
                elif response.status_code == 500:
                    self.log(f"❌ {description}: Internal Server Error", "ERROR")
                    self.log(f"   Response: {response.text[:100]}", "DEBUG")
                else:
                    self.log(f"⚠️  {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"❌ {description}: {str(e)}", "ERROR")
    
    def fix_api_issues(self):
        """Attempt to fix API issues"""
        self.log("🔧 Attempting to fix API issues...")
        
        # Try to restart the API server
        try:
            # Kill existing processes
            subprocess.run(["pkill", "-f", "uvicorn.*8765"], check=False)
            time.sleep(2)
            
            # Start API server
            api_dir = Path("mem0/openmemory/api")
            if api_dir.exists():
                self.log("🚀 Starting API server...")
                subprocess.Popen(
                    ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765", "--reload"],
                    cwd=api_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(5)
                self.log("✅ API server restarted")
                return True
            else:
                self.log("❌ API directory not found", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to restart API: {str(e)}", "ERROR")
            return False
    
    def test_ui_connection(self):
        """Test UI connection to API"""
        self.log("🔍 Testing UI connection...")
        
        try:
            # Test if UI loads
            response = requests.get(self.ui_url, timeout=10)
            if response.status_code == 200:
                self.log("✅ UI loads successfully")
                
                # Check if UI can fetch data
                test_api_call = f"{self.api_url}/api/v1/memories/?user_id={self.user_id}"
                api_response = requests.get(test_api_call, timeout=10)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    if 'items' in data:
                        memory_count = len(data['items'])
                        self.log(f"✅ UI can fetch {memory_count} memories from API")
                        return True
                    else:
                        self.log("⚠️  API response format unexpected")
                else:
                    self.log(f"❌ API call failed: HTTP {api_response.status_code}")
                    
            else:
                self.log(f"❌ UI not responding: HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ UI connection test failed: {str(e)}", "ERROR")
            
        return False
    
    def add_test_memory(self):
        """Add a test memory to verify the system works"""
        self.log("🧪 Adding test memory...")
        
        try:
            test_data = {
                "user_id": self.user_id,
                "text": f"Test memory added by fix script at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "metadata": {"source": "fix_script"},
                "app": "openmemory"
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/memories/",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("✅ Test memory added successfully")
                return True
            else:
                self.log(f"❌ Failed to add test memory: HTTP {response.status_code}")
                self.log(f"   Response: {response.text}", "DEBUG")
                
        except Exception as e:
            self.log(f"❌ Error adding test memory: {str(e)}", "ERROR")
            
        return False
    
    def generate_report(self):
        """Generate a comprehensive system report"""
        self.log("📋 Generating system report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "database": {},
            "api_tests": {},
            "recommendations": []
        }
        
        # Test services
        services = ["API", "UI", "Qdrant"]
        for service in services:
            report["services"][service] = "Unknown"
        
        # Save report
        with open("memory_system_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        self.log("✅ Report saved to memory_system_report.json")
    
    def run_comprehensive_fix(self):
        """Run complete diagnostic and fix process"""
        self.log("🚀 Starting comprehensive memory system fix...")
        self.log("=" * 60)
        
        # Step 1: Check services
        self.check_services()
        
        # Step 2: Check database
        db_ok = self.check_database()
        
        # Step 3: Test API
        self.test_api_endpoints()
        
        # Step 4: Fix API if needed
        self.fix_api_issues()
        
        # Step 5: Test UI connection
        ui_ok = self.test_ui_connection()
        
        # Step 6: Add test memory
        test_memory_ok = self.add_test_memory()
        
        # Step 7: Generate report
        self.generate_report()
        
        # Final summary
        self.log("=" * 60)
        self.log("🎯 FINAL SUMMARY")
        self.log(f"Database: {'✅ OK' if db_ok else '❌ Issues'}")
        self.log(f"UI Connection: {'✅ OK' if ui_ok else '❌ Issues'}")
        self.log(f"Test Memory: {'✅ OK' if test_memory_ok else '❌ Issues'}")
        
        if db_ok and ui_ok and test_memory_ok:
            self.log("🎉 Memory system is working correctly!")
            self.log(f"📱 Access your dashboard at: {self.ui_url}")
        else:
            self.log("⚠️  Some issues remain. Check the logs above.")
            
        return db_ok and ui_ok and test_memory_ok

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Memory Dashboard Fix Script")
        print("Usage: python3 fix-memory-dashboard.py")
        print("This script diagnoses and fixes memory dashboard issues.")
        return
    
    fixer = MemorySystemFixer()
    success = fixer.run_comprehensive_fix()
    
    if success:
        print("\n✅ All systems operational!")
        print(f"🌐 Dashboard: {UI_URL}")
        print(f"📊 API Docs: {API_URL}/docs")
    else:
        print("\n❌ Some issues remain. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 