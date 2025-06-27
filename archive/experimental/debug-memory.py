#!/usr/bin/env python3
"""
Debug script to identify memory system issues
"""

import sys
import requests
import os

def main():
    print("🔍 Memory System Debug")
    print("=" * 40)
    
    # Test 1: Basic Python
    print("✅ Python working")
    
    # Test 2: Check API connectivity
    api_url = "http://localhost:8765/api/v1"
    print(f"🔗 Testing API connection: {api_url}")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        print(f"✅ API Health: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API Connection Failed: localhost:8765 not responding")
        print("💡 This means the OpenMemory API server is not running")
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    # Test 3: Try to add a memory
    print("\n📝 Testing memory addition...")
    try:
        data = {"text": "Debug test memory", "user_id": "drj"}
        response = requests.post(f"{api_url}/memories/", json=data, timeout=5)
        print(f"✅ Memory add response: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Memory add failed: API server not running")
    except Exception as e:
        print(f"❌ Memory add error: {e}")
    
    # Test 4: Check if UI server components exist
    print("\n📁 Checking UI files...")
    files_to_check = [
        "simple-memory-ui.html",
        "memory-ui-server.py",
        "cursor-memory-enhanced.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
    
    print("\n🎯 Diagnosis:")
    print("The main issue is likely that the OpenMemory API server")
    print("at localhost:8765 is not running.")
    print("\n💡 Solutions:")
    print("1. Start OpenMemory services: docker-compose up -d")
    print("2. Or use the standalone UI server: python3 memory-ui-server.py")
    print("3. Check if Docker is running: docker ps")

if __name__ == "__main__":
    main() 