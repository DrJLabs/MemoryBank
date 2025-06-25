#!/usr/bin/env python3
"""
Cursor Memory Integration for OpenMemory
This script provides memory functionality for Cursor AI without MCP
"""

import sys
import json
import requests
from typing import List, Dict, Any

API_URL = "http://localhost:8765/api/v1"
USER_ID = "drj"


class MemoryClient:
    def __init__(self, api_url: str = API_URL, user_id: str = USER_ID):
        self.api_url = api_url
        self.user_id = user_id
        self.headers = {"Content-Type": "application/json"}

    def add_memory(self, text: str) -> Dict[str, Any]:
        """Add a new memory"""
        endpoint = f"{self.api_url}/memories/"
        data = {"text": text, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def search_memories(self, query: str) -> Dict[str, Any]:
        """Search memories"""
        endpoint = f"{self.api_url}/memories/filter"
        data = {"query": query, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def format_memory_response(self, memories: Dict[str, Any]) -> str:
        """Format memory response for display"""
        if "error" in memories:
            return f"Error: {memories['error']}"
        
        if "items" not in memories:
            return "No memories found."
        
        result = []
        for memory in memories.get("items", []):
            result.append(f"- {memory.get('content', 'Unknown')}")
        
        return "\n".join(result) if result else "No memories found."


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: cursor-memory-integration.py <command> [args]")
        print("Commands:")
        print("  add <text>     - Add a memory")
        print("  search <query> - Search memories")
        print("  remember <text> - Alias for add")
        print("  recall <query>  - Alias for search")
        sys.exit(1)
    
    client = MemoryClient()
    command = sys.argv[1].lower()
    
    if command in ["add", "remember"]:
        if len(sys.argv) < 3:
            print("Error: Please provide text to remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = client.add_memory(text)
        
        if "error" not in result:
            print(f"✅ Memory added: {result.get('content', text)}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command in ["search", "recall"]:
        if len(sys.argv) < 3:
            print("Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        memories = client.search_memories(query)
        
        print(f"🔍 Searching for: {query}")
        print("📋 Memories found:")
        print(client.format_memory_response(memories))
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'add', 'search', 'remember', or 'recall'")
        sys.exit(1)


if __name__ == "__main__":
    main() 