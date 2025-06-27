#!/usr/bin/env python3
"""
Comprehensive Port Management System
Tracks occupied localhost ports, finds available ones, maintains running list
"""

import socket
import json
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional

PORT_REGISTRY = "/tmp/cursor-port-registry.json"
COMMON_PORTS = [3000, 3001, 3010, 5000, 5001, 8000, 8001, 8080, 8081, 8765, 9000, 9001]

class PortManager:
    def __init__(self):
        self.registry_file = PORT_REGISTRY
        self.load_registry()
    
    def load_registry(self):
        """Load existing port registry or create new one"""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r') as f:
                    self.registry = json.load(f)
            else:
                self.registry = {
                    "occupied_ports": {},
                    "available_ports": [],
                    "last_updated": "",
                    "services": {}
                }
        except Exception as e:
            print(f"⚠️  Error loading registry: {e}")
            self.registry = {"occupied_ports": {}, "available_ports": [], "last_updated": "", "services": {}}
    
    def save_registry(self):
        """Save current registry to file"""
        try:
            self.registry["last_updated"] = datetime.now().isoformat()
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving registry: {e}")
    
    def is_port_available(self, port: int, host: str = "127.0.0.1") -> bool:
        """Check if a specific port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    def scan_ports(self, start_port: int = 3000, end_port: int = 9999) -> Dict[str, List[int]]:
        """Scan range of ports to find occupied and available ones"""
        occupied = []
        available = []
        
        print(f"🔍 Scanning ports {start_port}-{end_port}...")
        
        # Check common ports first
        for port in COMMON_PORTS:
            if start_port <= port <= end_port:
                if self.is_port_available(port):
                    available.append(port)
                else:
                    occupied.append(port)
        
        # Sample additional ports to avoid full scan
        sample_ports = list(range(start_port, min(start_port + 100, end_port), 10))
        for port in sample_ports:
            if port not in COMMON_PORTS:
                if self.is_port_available(port):
                    available.append(port)
                else:
                    occupied.append(port)
        
        return {"occupied": sorted(occupied), "available": sorted(available)}
    
    def get_processes_on_ports(self) -> Dict[int, str]:
        """Get processes running on specific ports"""
        port_processes = {}
        try:
            # Try multiple commands to get port info
            commands = [
                "ss -tulpn 2>/dev/null | grep LISTEN",
                "netstat -tulpn 2>/dev/null | grep LISTEN", 
                "lsof -i TCP -P -n 2>/dev/null | grep LISTEN"
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                    if result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            # Parse port info from different command outputs
                            if ':' in line and 'LISTEN' in line:
                                parts = line.split()
                                for part in parts:
                                    if ':' in part and part.split(':')[-1].isdigit():
                                        port = int(part.split(':')[-1])
                                        process_info = ' '.join(parts[-2:]) if len(parts) > 2 else "unknown"
                                        port_processes[port] = process_info
                        break  # Use first successful command
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️  Could not get process info: {e}")
        
        return port_processes
    
    def update_registry(self):
        """Update the port registry with current port status"""
        print("🔄 Updating port registry...")
        
        # Scan current port status
        port_status = self.scan_ports()
        process_info = self.get_processes_on_ports()
        
        # Update registry
        self.registry["occupied_ports"] = {}
        for port in port_status["occupied"]:
            self.registry["occupied_ports"][str(port)] = {
                "process": process_info.get(port, "unknown"),
                "detected_at": datetime.now().isoformat()
            }
        
        self.registry["available_ports"] = port_status["available"]
        
        # Save updated registry
        self.save_registry()
        
        return port_status
    
    def find_available_port(self, requested_port: int = None) -> int:
        """Find an available port, preferring the requested one"""
        # Update registry first
        self.update_registry()
        
        # Check requested port first
        if requested_port and self.is_port_available(requested_port):
            return requested_port
        
        # Find from available ports
        available_ports = self.registry.get("available_ports", [])
        if available_ports:
            return available_ports[0]
        
        # Fallback: scan for any available port
        for port in range(8080, 8200):
            if self.is_port_available(port):
                return port
        
        raise Exception("No available ports found")
    
    def register_service(self, service_name: str, port: int, description: str = ""):
        """Register a service using a specific port"""
        self.registry["services"][service_name] = {
            "port": port,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "status": "running"
        }
        self.save_registry()
    
    def unregister_service(self, service_name: str):
        """Unregister a service"""
        if service_name in self.registry["services"]:
            del self.registry["services"][service_name]
            self.save_registry()
    
    def get_service_port(self, service_name: str) -> Optional[int]:
        """Get the port for a registered service"""
        service = self.registry["services"].get(service_name)
        return service["port"] if service else None
    
    def print_status(self):
        """Print current port status"""
        print("\n📊 LOCALHOST PORT STATUS")
        print("=" * 50)
        
        # Occupied ports
        occupied = self.registry.get("occupied_ports", {})
        if occupied:
            print("🔴 OCCUPIED PORTS:")
            for port, info in occupied.items():
                process = info.get("process", "unknown")[:30]
                print(f"   {port}: {process}")
        
        # Available ports  
        available = self.registry.get("available_ports", [])[:10]
        if available:
            print(f"\n🟢 AVAILABLE PORTS (showing first 10): {', '.join(map(str, available))}")
        
        # Registered services
        services = self.registry.get("services", {})
        if services:
            print("\n🔧 REGISTERED SERVICES:")
            for name, info in services.items():
                port = info.get("port", "unknown")
                desc = info.get("description", "")
                print(f"   {name}: port {port} - {desc}")
        
        print("=" * 50)

def main():
    """Main port management function"""
    import sys
    
    if len(sys.argv) < 2:
        print("🔧 Port Manager - Localhost Port Management System")
        print("=" * 55)
        print("Commands:")
        print("  scan                    - Scan and update port registry")
        print("  status                  - Show current port status")
        print("  find <port>            - Find available port (optionally preferred)")
        print("  register <name> <port> - Register service on port")
        print("  unregister <name>      - Unregister service")
        print("  get <name>             - Get port for service")
        return
    
    manager = PortManager()
    command = sys.argv[1].lower()
    
    if command == "scan":
        manager.update_registry()
        manager.print_status()
    
    elif command == "status":
        manager.print_status()
    
    elif command == "find":
        requested_port = int(sys.argv[2]) if len(sys.argv) > 2 else None
        try:
            available_port = manager.find_available_port(requested_port)
            print(f"✅ Available port: {available_port}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif command == "register":
        if len(sys.argv) < 4:
            print("❌ Usage: register <service_name> <port> [description]")
            return
        
        service_name = sys.argv[2]
        port = int(sys.argv[3])
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        
        manager.register_service(service_name, port, description)
        print(f"✅ Registered {service_name} on port {port}")
    
    elif command == "unregister":
        if len(sys.argv) < 3:
            print("❌ Usage: unregister <service_name>")
            return
        
        service_name = sys.argv[2]
        manager.unregister_service(service_name)
        print(f"✅ Unregistered {service_name}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ Usage: get <service_name>")
            return
        
        service_name = sys.argv[2]
        port = manager.get_service_port(service_name)
        if port:
            print(f"✅ {service_name} is on port {port}")
        else:
            print(f"❌ Service {service_name} not found")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 