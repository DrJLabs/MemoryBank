"""
Reset Manager for Mem0 Memory System

Provides comprehensive reset functionality with fine-grained control over
what gets reset (vector store, graph store, history, etc.)
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


class ResetScope(Enum):
    """Defines what components to reset"""
    ALL = "all"
    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    HISTORY_ONLY = "history_only"
    VECTOR_AND_HISTORY = "vector_and_history"
    GRAPH_AND_HISTORY = "graph_and_history"


@dataclass
class ResetOptions:
    """Configuration for reset operation"""
    scope: ResetScope = ResetScope.ALL
    force: bool = False  # Skip confirmation prompts
    dry_run: bool = False  # Preview what would be deleted
    preserve_filters: Optional[Dict[str, Any]] = None  # Preserve memories matching filters
    
    @classmethod
    def from_cli_args(cls, keep_vector: bool = False, keep_graph: bool = False, 
                      keep_history: bool = False, force: bool = False, 
                      dry_run: bool = False, preserve_filters: Optional[Dict[str, Any]] = None):
        """Create ResetOptions from CLI arguments"""
        # Determine scope based on what to keep
        if keep_vector and keep_graph and not keep_history:
            scope = ResetScope.HISTORY_ONLY
        elif keep_vector and not keep_graph and not keep_history:
            scope = ResetScope.GRAPH_AND_HISTORY
        elif not keep_vector and keep_graph and not keep_history:
            scope = ResetScope.VECTOR_AND_HISTORY
        elif not keep_vector and not keep_graph and keep_history:
            scope = ResetScope.VECTOR_ONLY  # Special case: only reset vector
        elif keep_vector and not keep_graph and keep_history:
            scope = ResetScope.GRAPH_ONLY
        else:
            scope = ResetScope.ALL
            
        return cls(
            scope=scope,
            force=force,
            dry_run=dry_run,
            preserve_filters=preserve_filters
        )


class ResetManager:
    """Manages reset operations for the memory system"""
    
    def __init__(self, vector_store=None, graph_store=None, db=None):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.db = db
        self._lock = threading.RLock()
        
    def get_reset_summary(self, options: ResetOptions) -> Dict[str, Any]:
        """Get a summary of what would be reset"""
        summary = {
            "scope": options.scope.value,
            "components_to_reset": [],
            "estimated_deletions": {}
        }
        
        with self._lock:
            # Check vector store
            if options.scope in [ResetScope.ALL, ResetScope.VECTOR_ONLY, ResetScope.VECTOR_AND_HISTORY]:
                summary["components_to_reset"].append("vector_store")
                if self.vector_store:
                    try:
                        # Get count of vectors
                        all_memories = self.vector_store.list(filters={}, limit=None)
                        if isinstance(all_memories, tuple):
                            all_memories = all_memories[0]
                        summary["estimated_deletions"]["vector_memories"] = len(all_memories)
                    except Exception as e:
                        logger.warning(f"Could not get vector count: {e}")
                        summary["estimated_deletions"]["vector_memories"] = "unknown"
            
            # Check graph store
            if options.scope in [ResetScope.ALL, ResetScope.GRAPH_ONLY, ResetScope.GRAPH_AND_HISTORY]:
                summary["components_to_reset"].append("graph_store")
                if self.graph_store:
                    try:
                        # This is an estimate - actual implementation would query graph
                        summary["estimated_deletions"]["graph_nodes"] = "all nodes and relationships"
                    except Exception as e:
                        logger.warning(f"Could not get graph info: {e}")
                        summary["estimated_deletions"]["graph_nodes"] = "unknown"
            
            # Check history database
            if options.scope in [ResetScope.ALL, ResetScope.HISTORY_ONLY, ResetScope.VECTOR_AND_HISTORY, 
                                ResetScope.GRAPH_AND_HISTORY]:
                summary["components_to_reset"].append("history_database")
                if self.db:
                    try:
                        # Get history count
                        cur = self.db.connection.execute("SELECT COUNT(*) FROM history")
                        count = cur.fetchone()[0]
                        summary["estimated_deletions"]["history_entries"] = count
                    except Exception as e:
                        logger.warning(f"Could not get history count: {e}")
                        summary["estimated_deletions"]["history_entries"] = "unknown"
                        
        return summary
    
    def reset(self, options: ResetOptions) -> Dict[str, Any]:
        """Execute reset based on options"""
        if options.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "summary": self.get_reset_summary(options)
            }
            
        results = {
            "success": True,
            "components_reset": [],
            "errors": []
        }
        
        with self._lock:
            # Reset vector store
            if options.scope in [ResetScope.ALL, ResetScope.VECTOR_ONLY, ResetScope.VECTOR_AND_HISTORY]:
                try:
                    if self.vector_store:
                        logger.info("Resetting vector store...")
                        if options.preserve_filters:
                            # Delete selectively
                            self._selective_vector_delete(options.preserve_filters)
                        else:
                            # Full reset
                            self.vector_store.delete_col()
                        results["components_reset"].append("vector_store")
                except Exception as e:
                    logger.error(f"Failed to reset vector store: {e}")
                    results["errors"].append(f"vector_store: {str(e)}")
                    results["success"] = False
            
            # Reset graph store
            if options.scope in [ResetScope.ALL, ResetScope.GRAPH_ONLY, ResetScope.GRAPH_AND_HISTORY]:
                try:
                    if self.graph_store:
                        logger.info("Resetting graph store...")
                        if options.preserve_filters:
                            # Delete selectively
                            self._selective_graph_delete(options.preserve_filters)
                        else:
                            # Full reset - delete ALL nodes and relationships
                            self._full_graph_reset()
                        results["components_reset"].append("graph_store")
                except Exception as e:
                    logger.error(f"Failed to reset graph store: {e}")
                    results["errors"].append(f"graph_store: {str(e)}")
                    results["success"] = False
            
            # Reset history database
            if options.scope in [ResetScope.ALL, ResetScope.HISTORY_ONLY, ResetScope.VECTOR_AND_HISTORY, 
                                ResetScope.GRAPH_AND_HISTORY]:
                try:
                    if self.db:
                        logger.info("Resetting history database...")
                        self.db.connection.execute("BEGIN")
                        self.db.connection.execute("DROP TABLE IF EXISTS history")
                        self.db.connection.execute("COMMIT")
                        self.db._create_history_table()
                        results["components_reset"].append("history_database")
                except Exception as e:
                    logger.error(f"Failed to reset history: {e}")
                    if self.db:
                        self.db.connection.execute("ROLLBACK")
                    results["errors"].append(f"history_database: {str(e)}")
                    results["success"] = False
                    
        return results
    
    def _selective_vector_delete(self, preserve_filters: Dict[str, Any]):
        """Delete vectors except those matching preserve filters"""
        # Get all memories
        all_memories = self.vector_store.list(filters={}, limit=None)
        if isinstance(all_memories, tuple):
            all_memories = all_memories[0]
            
        # Get memories to preserve
        preserve_memories = self.vector_store.list(filters=preserve_filters, limit=None)
        if isinstance(preserve_memories, tuple):
            preserve_memories = preserve_memories[0]
        
        preserve_ids = {m.id for m in preserve_memories}
        
        # Delete non-preserved memories
        for memory in all_memories:
            if memory.id not in preserve_ids:
                self.vector_store.delete(vector_id=memory.id)
    
    def _selective_graph_delete(self, preserve_filters: Dict[str, Any]):
        """Delete graph nodes except those matching preserve filters"""
        # Build NOT condition for filters
        not_conditions = []
        params = {}
        
        for key, value in preserve_filters.items():
            not_conditions.append(f"NOT n.{key} = ${key}")
            params[key] = value
        
        if not_conditions:
            where_clause = "WHERE " + " OR ".join(not_conditions)
        else:
            where_clause = ""
            
        # Delete nodes not matching preserve filters
        cypher = f"""
        MATCH (n)
        {where_clause}
        DETACH DELETE n
        """
        
        self.graph_store.graph.query(cypher, params=params)
    
    def _full_graph_reset(self):
        """Completely reset the graph store - delete ALL nodes and relationships"""
        # This is the TRUE reset - delete everything regardless of filters
        logger.warning("Executing full graph reset - ALL nodes and relationships will be deleted")
        
        cypher = """
        MATCH (n)
        DETACH DELETE n
        """
        
        self.graph_store.graph.query(cypher, params={})
        
        # For completeness, also try to drop indexes if they exist
        # This is graph-database specific
        try:
            if hasattr(self.graph_store.graph, 'query'):
                # Try to drop indexes (Neo4j specific)
                self.graph_store.graph.query("SHOW INDEXES", params={})
                # Parse and drop each index...
                # This would be implementation specific
        except Exception as e:
            logger.debug(f"Could not drop indexes (may not be supported): {e}")


class AsyncResetManager(ResetManager):
    """Async version of ResetManager"""
    
    async def get_reset_summary_async(self, options: ResetOptions) -> Dict[str, Any]:
        """Get a summary of what would be reset (async)"""
        return await asyncio.to_thread(self.get_reset_summary, options)
    
    async def reset_async(self, options: ResetOptions) -> Dict[str, Any]:
        """Execute reset based on options (async)"""
        return await asyncio.to_thread(self.reset, options) 