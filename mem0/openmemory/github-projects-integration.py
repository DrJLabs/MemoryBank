#!/usr/bin/env python3
"""
GitHub Projects Integration for MemoryBank System
Automated project management using GitHub Projects API
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GitHubConfig:
    """GitHub Projects configuration"""
    token: str
    org: str = "DrJLabs"
    repo: str = "MemoryBank"
    project_number: int = 1

class GitHubProjectsAPI:
    """GitHub Projects GraphQL API client"""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
            "X-Github-Next-Global-ID": "1"
        }
        self.api_url = "https://api.github.com/graphql"
    
    def execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_project_info(self) -> Dict:
        """Get project information and fields"""
        query = """
        query($org: String!, $number: Int!) {
            organization(login: $org) {
                projectV2(number: $number) {
                    id
                    title
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2Field {
                                id
                                name
                                dataType
                            }
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"org": self.config.org, "number": self.config.project_number}
        result = self.execute_query(query, variables)
        return result.get("data", {}).get("organization", {}).get("projectV2", {})
    
    def create_issue(self, title: str, body: str) -> Dict:
        """Create new issue"""
        mutation = """
        mutation($repositoryId: ID!, $title: String!, $body: String) {
            createIssue(input: {repositoryId: $repositoryId, title: $title, body: $body}) {
                issue {
                    id
                    number
                    title
                    url
                }
            }
        }
        """
        
        repo_id = self._get_repository_id()
        variables = {"repositoryId": repo_id, "title": title, "body": body}
        
        result = self.execute_query(mutation, variables)
        return result.get("data", {}).get("createIssue", {}).get("issue", {})
    
    def _get_repository_id(self) -> str:
        """Get repository ID"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
            }
        }
        """
        
        variables = {"owner": self.config.org, "name": self.config.repo}
        result = self.execute_query(query, variables)
        return result.get("data", {}).get("repository", {}).get("id", "")

class MemoryProjectsSync:
    """Sync between MemoryBank and GitHub Projects"""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.github_api = GitHubProjectsAPI(config)
        self.memory_api_base = "http://localhost:8765"
    
    async def sync_insights(self):
        """Sync memory insights to GitHub Projects"""
        logger.info("Syncing memory insights to GitHub Projects...")
        
        try:
            insights = await self._get_memory_insights()
            
            for insight in insights:
                await self._create_issue_from_insight(insight)
                
        except Exception as e:
            logger.error(f"Sync error: {e}")
    
    async def _get_memory_insights(self) -> List[Dict]:
        """Get insights from MemoryBank API"""
        try:
            response = requests.get(f"{self.memory_api_base}/api/memories")
            response.raise_for_status()
            memories = response.json()
            
            # Filter actionable insights
            actionable = []
            for memory in memories.get("memories", []):
                content = memory.get("content", "").lower()
                if any(keyword in content for keyword in [
                    "bug", "error", "performance", "optimization", "improvement"
                ]):
                    actionable.append(memory)
            
            return actionable[:3]  # Limit to 3 most recent
            
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return []
    
    async def _create_issue_from_insight(self, insight: Dict):
        """Create GitHub issue from memory insight"""
        try:
            content = insight.get("content", "")
            title = self._generate_title(content)
            body = self._generate_body(content, insight)
            
            issue = self.github_api.create_issue(title, body)
            
            if issue:
                logger.info(f"Created issue: {issue.get('title')} (#{issue.get('number')})")
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
    
    def _generate_title(self, content: str) -> str:
        """Generate issue title from content"""
        # Extract first sentence
        first_sentence = content.split(".")[0].strip()
        
        if len(first_sentence) > 60:
            first_sentence = first_sentence[:57] + "..."
        
        # Add prefix based on content type
        if "error" in content.lower() or "bug" in content.lower():
            return f"🐛 Fix: {first_sentence}"
        elif "performance" in content.lower():
            return f"⚡ Optimize: {first_sentence}"
        else:
            return f"✨ Enhance: {first_sentence}"
    
    def _generate_body(self, content: str, insight: Dict) -> str:
        """Generate issue body from insight"""
        timestamp = insight.get("timestamp", "Unknown")
        
        return f"""## Memory Insight Analysis

**Source**: MemoryBank System
**Timestamp**: {timestamp}
**Insight ID**: {insight.get("id", "Unknown")}

## Content
{content}

## Recommended Actions
- [ ] Analyze the issue
- [ ] Implement solution
- [ ] Test changes
- [ ] Update documentation

---
*Auto-generated from MemoryBank insight*"""

# Main service class
class GitHubProjectsService:
    """Main GitHub Projects integration service"""
    
    def __init__(self):
        self.config = self._load_config()
        self.sync_service = MemoryProjectsSync(self.config)
    
    def _load_config(self) -> GitHubConfig:
        """Load configuration from environment"""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        
        return GitHubConfig(
            token=token,
            org=os.getenv("GITHUB_ORG", "DrJLabs"),
            repo=os.getenv("GITHUB_REPO", "MemoryBank"),
            project_number=int(os.getenv("GITHUB_PROJECT_NUMBER", "1"))
        )
    
    async def start(self):
        """Start the integration service"""
        logger.info("Starting GitHub Projects integration...")
        
        # Test connection
        project_info = self.github_api.get_project_info()
        if project_info:
            logger.info(f"Connected to project: {project_info.get('title')}")
        
        # Run continuous sync
        while True:
            await self.sync_service.sync_insights()
            await asyncio.sleep(900)  # 15 minutes

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing GitHub Projects connection...")
        try:
            service = GitHubProjectsService()
            project_info = service.sync_service.github_api.get_project_info()
            print(f"✅ Connected to: {project_info.get('title', 'Unknown project')}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    else:
        service = GitHubProjectsService()
        try:
            asyncio.run(service.start())
        except KeyboardInterrupt:
            print("\n⏹️ Service stopped") 