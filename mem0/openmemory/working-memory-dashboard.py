#!/usr/bin/env python3
"""
Working Memory Dashboard
A functional dashboard that bypasses the broken OpenMemory API
and works directly with the mem-search system
"""

import sys
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

PORT = 8082
USER_ID = "drj"

class MemoryDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urlparse(self.path).path
            query = parse_qs(urlparse(self.path).query)
            
            if path == '/':
                self.serve_dashboard()
            elif path == '/api/memories':
                self.serve_memories_api()
            elif path == '/api/add':
                self.serve_add_memory_api(query)
            elif path == '/api/search':
                self.serve_search_api(query)
            else:
                self.send_error(404)
        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_error(500)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = urlparse(self.path).path
            
            if path == '/api/add':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                self.handle_add_memory(data)
            else:
                self.send_error(404)
        except Exception as e:
            print(f"Error handling POST: {e}")
            self.send_error(500)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Working Memory Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a; color: #e4e4e7; line-height: 1.6;
        }
        .header { 
            background: #18181b; padding: 1rem 2rem; border-bottom: 1px solid #27272a;
            display: flex; justify-content: space-between; align-items: center;
        }
        .logo { font-size: 1.5rem; font-weight: bold; color: #06b6d4; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .stats { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem; margin-bottom: 2rem;
        }
        .stat-card {
            background: #18181b; padding: 1.5rem; border-radius: 8px;
            border: 1px solid #27272a;
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #06b6d4; }
        .stat-label { color: #a1a1aa; margin-top: 0.5rem; }
        .controls {
            display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;
        }
        .btn {
            padding: 0.5rem 1rem; border: none; border-radius: 6px;
            cursor: pointer; font-size: 0.9rem; transition: all 0.2s;
        }
        .btn-primary { background: #06b6d4; color: white; }
        .btn-primary:hover { background: #0891b2; }
        .btn-secondary { background: #27272a; color: #e4e4e7; }
        .btn-secondary:hover { background: #3f3f46; }
        .search-box {
            flex: 1; padding: 0.5rem; border: 1px solid #27272a;
            background: #18181b; color: #e4e4e7; border-radius: 6px;
        }
        .memories-list { background: #18181b; border-radius: 8px; border: 1px solid #27272a; }
        .memory-item {
            padding: 1rem; border-bottom: 1px solid #27272a;
            transition: background 0.2s;
        }
        .memory-item:hover { background: #1f1f23; }
        .memory-item:last-child { border-bottom: none; }
        .memory-content { margin-bottom: 0.5rem; }
        .memory-meta { color: #a1a1aa; font-size: 0.85rem; }
        .loading { text-align: center; padding: 2rem; color: #a1a1aa; }
        .error { color: #ef4444; background: #18181b; padding: 1rem; border-radius: 6px; margin: 1rem 0; }
        .success { color: #22c55e; background: #18181b; padding: 1rem; border-radius: 6px; margin: 1rem 0; }
        .add-memory { 
            background: #18181b; padding: 1.5rem; border-radius: 8px;
            border: 1px solid #27272a; margin-bottom: 2rem;
        }
        .add-memory textarea {
            width: 100%; padding: 0.75rem; border: 1px solid #27272a;
            background: #0a0a0a; color: #e4e4e7; border-radius: 6px;
            resize: vertical; min-height: 80px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🧠 Working Memory Dashboard</div>
        <div>
            <button class="btn btn-secondary" onclick="refreshMemories()">🔄 Refresh</button>
            <span id="status" style="margin-left: 1rem; color: #22c55e;">● Connected</span>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalMemories">-</div>
                <div class="stat-label">Total Memories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="lastUpdated">-</div>
                <div class="stat-label">Last Updated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">✅</div>
                <div class="stat-label">System Status</div>
            </div>
        </div>
        
        <div class="add-memory">
            <h3 style="margin-bottom: 1rem;">Add New Memory</h3>
            <textarea id="newMemoryText" placeholder="Enter your memory here..."></textarea>
            <div style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="addMemory()">Add Memory</button>
                <button class="btn btn-secondary" onclick="clearForm()">Clear</button>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="Search memories..." 
                   onkeyup="searchMemories()" />
            <button class="btn btn-secondary" onclick="searchMemories()">🔍 Search</button>
            <button class="btn btn-secondary" onclick="showAllMemories()">📋 Show All</button>
        </div>
        
        <div id="messages"></div>
        
        <div class="memories-list">
            <div id="memoriesContainer" class="loading">
                Loading memories...
            </div>
        </div>
    </div>

    <script>
        let allMemories = [];
        
        async function loadMemories() {
            try {
                const response = await fetch('/api/memories');
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                allMemories = data.memories || [];
                updateStats();
                displayMemories(allMemories);
                
            } catch (error) {
                showError('Failed to load memories: ' + error.message);
            }
        }
        
        function updateStats() {
            document.getElementById('totalMemories').textContent = allMemories.length;
            document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
        }
        
        function displayMemories(memories) {
            const container = document.getElementById('memoriesContainer');
            
            if (memories.length === 0) {
                container.innerHTML = '<div class="loading">No memories found.</div>';
                return;
            }
            
            container.innerHTML = memories.map((memory, index) => `
                <div class="memory-item">
                    <div class="memory-content">${escapeHtml(memory)}</div>
                    <div class="memory-meta">Memory #${index + 1}</div>
                </div>
            `).join('');
        }
        
        function searchMemories() {
            const query = document.getElementById('searchBox').value.trim();
            
            if (!query) {
                displayMemories(allMemories);
                return;
            }
            
            const filtered = allMemories.filter(memory => 
                memory.toLowerCase().includes(query.toLowerCase())
            );
            
            displayMemories(filtered);
        }
        
        function showAllMemories() {
            document.getElementById('searchBox').value = '';
            displayMemories(allMemories);
        }
        
        async function addMemory() {
            const text = document.getElementById('newMemoryText').value.trim();
            
            if (!text) {
                showError('Please enter some text for the memory.');
                return;
            }
            
            try {
                const response = await fetch('/api/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showSuccess('Memory added successfully!');
                    document.getElementById('newMemoryText').value = '';
                    setTimeout(loadMemories, 1000);
                } else {
                    showError(result.error || 'Failed to add memory');
                }
                
            } catch (error) {
                showError('Failed to add memory: ' + error.message);
            }
        }
        
        function clearForm() {
            document.getElementById('newMemoryText').value = '';
        }
        
        function refreshMemories() {
            loadMemories();
        }
        
        function showError(message) {
            const messages = document.getElementById('messages');
            messages.innerHTML = `<div class="error">❌ ${escapeHtml(message)}</div>`;
            setTimeout(() => messages.innerHTML = '', 5000);
        }
        
        function showSuccess(message) {
            const messages = document.getElementById('messages');
            messages.innerHTML = `<div class="success">✅ ${escapeHtml(message)}</div>`;
            setTimeout(() => messages.innerHTML = '', 3000);
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Initialize
        loadMemories();
        
        // Auto-refresh every 30 seconds
        setInterval(loadMemories, 30000);
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_memories_api(self):
        """API endpoint to get memories"""
        try:
            # Use the mem-search system directly
            result = subprocess.run(
                ['python3', 'mem0/openmemory/cursor-memory-enhanced.py', 'search', ''],
                capture_output=True, text=True, cwd='/home/drj/*C-System/MemoryBank'
            )
            
            if result.returncode == 0:
                # Parse the output to extract memories
                lines = result.stdout.strip().split('\n')
                memories = []
                
                for line in lines:
                    if line.startswith(('- ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                        # Remove numbering and clean up
                        memory = line.split('. ', 1)[-1] if '. ' in line else line[2:]
                        memories.append(memory)
                
                response = {"memories": memories, "total": len(memories)}
            else:
                response = {"error": "Failed to retrieve memories", "memories": []}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_add_memory(self, data):
        """Handle adding a new memory"""
        try:
            text = data.get('text', '').strip()
            if not text:
                raise ValueError("No text provided")
            
            # Use the mem-add command
            result = subprocess.run(
                ['python3', 'mem0/openmemory/cursor-memory-enhanced.py', 'add', text],
                capture_output=True, text=True, cwd='/home/drj/*C-System/MemoryBank'
            )
            
            if result.returncode == 0:
                response = {"success": True, "message": "Memory added successfully"}
            else:
                response = {"success": False, "error": result.stderr or "Failed to add memory"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

def find_available_port(start_port=8082):
    """Find an available port starting from start_port"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    global PORT
    
    # Find available port
    PORT = find_available_port(8082)
    if not PORT:
        print("❌ No available ports found")
        sys.exit(1)
    
    # Start server
    server = HTTPServer(('localhost', PORT), MemoryDashboardHandler)
    
    print(f"🚀 Working Memory Dashboard")
    print(f"📱 URL: http://localhost:{PORT}")
    print(f"🔗 Opening browser...")
    print(f"⚡ Press Ctrl+C to stop")
    
    # Open browser
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main() 