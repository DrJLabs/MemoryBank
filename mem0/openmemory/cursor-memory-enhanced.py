#!/usr/bin/env python3
"""
Enhanced Cursor Memory Integration for OpenMemory
Advanced features: project context, analytics, categorization, backup integration
"""

import sys
import json
import requests
import os
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

API_URL = "http://localhost:8765/api/v1"
USER_ID = "drj"


class EnhancedMemoryClient:
    def __init__(self, api_url: str = API_URL, user_id: str = USER_ID):
        self.api_url = api_url
        self.user_id = user_id
        self.headers = {"Content-Type": "application/json"}
        self.project_context = self._get_project_context()

    def _get_project_context(self) -> str:
        """Get current project context from pwd"""
        try:
            return f"[PROJECT:{os.path.basename(os.getcwd())}]"
        except:
            return "[PROJECT:unknown]"

    def add_memory(self, text: str, category: str = None, project_scope: bool = True) -> Dict[str, Any]:
        """Add a new memory with optional categorization and project context"""
        endpoint = f"{self.api_url}/memories/"
        
        # Add project context if enabled
        if project_scope and not text.startswith("[PROJECT:"):
            text = f"{self.project_context} {text}"
        
        # Add category tag if provided
        if category:
            text = f"[{category.upper()}] {text}"
        
        data = {"text": text, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def search_memories(self, query: str, project_only: bool = False) -> Dict[str, Any]:
        """Search memories with optional project filtering"""
        endpoint = f"{self.api_url}/memories/filter"
        
        # Add project context to query if requested
        if project_only:
            query = f"{self.project_context} {query}"
        
        data = {"query": query, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_analytics(self) -> Dict[str, Any]:
        """Get memory analytics and insights"""
        try:
            memories = self.search_memories("", project_only=False)
            if "error" in memories or "items" not in memories:
                return {"error": "Cannot fetch memories for analytics"}
            
            items = memories["items"]
            total_memories = len(items)
            
            # Extract categories from content
            categories = []
            projects = []
            for item in items:
                content = item.get("content", "")
                # Extract [CATEGORY] tags
                if content.startswith("[") and "]" in content:
                    tag = content.split("]")[0][1:]
                    if tag.startswith("PROJECT:"):
                        projects.append(tag.replace("PROJECT:", ""))
                    else:
                        categories.append(tag)
            
            return {
                "total_memories": total_memories,
                "top_categories": dict(Counter(categories).most_common(5)),
                "projects": list(set(projects)),
                "current_project": self.project_context.replace("[PROJECT:", "").replace("]", ""),
                "recent_memories": [item.get("content", "")[:50] + "..." for item in items[:3]]
            }
        except Exception as e:
            return {"error": str(e)}

    def format_memory_response(self, memories: Dict[str, Any], show_metadata: bool = False) -> str:
        """Format memory response for display with optional metadata"""
        if "error" in memories:
            return f"❌ Error: {memories['error']}"
        
        if "items" not in memories:
            return "📭 No memories found."
        
        result = []
        for i, memory in enumerate(memories.get("items", []), 1):
            content = memory.get('content', 'Unknown')
            if show_metadata:
                created = memory.get('created_at', 'Unknown')
                result.append(f"{i}. {content}")
                result.append(f"   📅 Created: {created}")
            else:
                result.append(f"{i}. {content}")
        
        return "\n".join(result) if result else "📭 No memories found."

    def backup_trigger(self) -> str:
        """Trigger a backup of the memory system"""
        try:
            import subprocess
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            backup_cmd = f"docker run --rm -v openmemory_mem0_storage:/data -v /tmp:/backup alpine tar czf /backup/mem0-backup-{timestamp}.tar.gz -C /data ."
            result = subprocess.run(backup_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"✅ Backup created: /tmp/mem0-backup-{timestamp}.tar.gz"
            else:
                return f"❌ Backup failed: {result.stderr}"
        except Exception as e:
            return f"❌ Backup error: {str(e)}"


def main():
    """Enhanced main function with additional commands"""
    if len(sys.argv) < 2:
        print("🧠 Enhanced Cursor Memory Integration")
        print("=====================================")
        print("Commands:")
        print("  add <text>           - Add a memory")
        print("  search <query>       - Search memories")
        print("  remember <text>      - Alias for add")
        print("  recall <query>       - Alias for search")
        print("  analytics           - Show memory analytics")
        print("  project-add <text>   - Add memory with project context")
        print("  project-search <q>   - Search current project only")
        print("  learn <text>         - Add as learning memory")
        print("  preference <text>    - Add as preference memory")
        print("  backup              - Create memory backup")
        sys.exit(1)
    
    client = EnhancedMemoryClient()
    command = sys.argv[1].lower()
    
    if command in ["add", "remember"]:
        if len(sys.argv) < 3:
            print("❌ Error: Please provide text to remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = client.add_memory(text)
        
        if "error" not in result:
            print(f"✅ Memory added: {result.get('content', text)}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command in ["search", "recall"]:
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        memories = client.search_memories(query)
        
        print(f"🔍 Searching for: {query}")
        print("📋 Memories found:")
        print(client.format_memory_response(memories))
    
    elif command == "analytics":
        analytics = client.get_analytics()
        if "error" not in analytics:
            print("📊 Memory Analytics:")
            print(f"📝 Total memories: {analytics['total_memories']}")
            print(f"🏷️  Top categories: {analytics['top_categories']}")
            print(f"📁 Projects: {', '.join(analytics['projects'])}")
            print(f"🎯 Current project: {analytics['current_project']}")
            print(f"🕒 Recent memories:")
            for memory in analytics['recent_memories']:
                print(f"   • {memory}")
        else:
            print(f"❌ Analytics error: {analytics['error']}")
    
    elif command == "project-add":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide text to remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = client.add_memory(text, project_scope=True)
        
        if "error" not in result:
            print(f"✅ Project memory added: {result.get('content', text)}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == "project-search":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        memories = client.search_memories(query, project_only=True)
        
        print(f"🔍 Searching in current project for: {query}")
        print("📋 Project memories found:")
        print(client.format_memory_response(memories))
    
    elif command == "learn":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide learning content")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = client.add_memory(text, category="LEARNING")
        
        if "error" not in result:
            print(f"📚 Learning added: {result.get('content', text)}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == "preference":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide preference content")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = client.add_memory(text, category="PREFERENCE")
        
        if "error" not in result:
            print(f"⚙️ Preference added: {result.get('content', text)}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == "backup":
        result = client.backup_trigger()
        print(result)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'add', 'search', 'analytics', 'project-add', 'learn', 'preference', or 'backup'")
        sys.exit(1)


if __name__ == "__main__":
    main() 