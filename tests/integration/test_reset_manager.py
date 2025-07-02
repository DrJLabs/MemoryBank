"""
Test Reset Manager Implementation for Mem0 Memory System

Tests the comprehensive reset functionality with various scopes and options.
"""

import pytest
from unittest.mock import Mock
from mem0.memory.reset_manager import (
    ResetManager, AsyncResetManager, ResetOptions, ResetScope
)


class TestResetOptions:
    """Test ResetOptions configuration"""
    
    def test_default_options(self):
        """Test default reset options"""
        options = ResetOptions()
        assert options.scope == ResetScope.ALL
        assert options.force is False
        assert options.dry_run is False
        assert options.preserve_filters is None
        
    def test_from_cli_args_all_keep(self):
        """Test CLI args when keeping everything"""
        options = ResetOptions.from_cli_args(
            keep_vector=True,
            keep_graph=True,
            keep_history=True
        )
        assert options.scope == ResetScope.ALL  # Nothing to reset
        
    def test_from_cli_args_keep_vector(self):
        """Test CLI args when keeping only vector"""
        options = ResetOptions.from_cli_args(keep_vector=True)
        assert options.scope == ResetScope.GRAPH_AND_HISTORY
        
    def test_from_cli_args_keep_graph(self):
        """Test CLI args when keeping only graph"""
        options = ResetOptions.from_cli_args(keep_graph=True)
        assert options.scope == ResetScope.VECTOR_AND_HISTORY
        
    def test_from_cli_args_keep_history(self):
        """Test CLI args when keeping only history"""
        options = ResetOptions.from_cli_args(keep_history=True)
        assert options.scope == ResetScope.VECTOR_ONLY
        
    def test_from_cli_args_with_filters(self):
        """Test CLI args with preserve filters"""
        filters = {"user_id": "test_user"}
        options = ResetOptions.from_cli_args(preserve_filters=filters)
        assert options.preserve_filters == filters


class TestResetManager:
    """Test ResetManager functionality"""
    
    @pytest.fixture
    def mock_stores(self):
        """Create mock stores for testing"""
        vector_store = Mock()
        graph_store = Mock()
        db = Mock()
        
        # Mock vector store methods
        vector_store.list.return_value = ([Mock(id=f"vec_{i}") for i in range(5)],)
        vector_store.delete_col = Mock()
        
        # Mock graph store methods
        graph_store.graph = Mock()
        graph_store.graph.query = Mock()
        
        # Mock database methods
        db.connection = Mock()
        db.connection.execute = Mock()
        db._create_history_table = Mock()
        
        return vector_store, graph_store, db
        
    def test_get_reset_summary_all(self, mock_stores):
        """Test getting reset summary for full reset"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        # Mock history count
        db.connection.execute.return_value.fetchone.return_value = [10]
        
        options = ResetOptions(scope=ResetScope.ALL)
        summary = manager.get_reset_summary(options)
        
        assert "vector_store" in summary["components_to_reset"]
        assert "graph_store" in summary["components_to_reset"]
        assert "history_database" in summary["components_to_reset"]
        assert summary["estimated_deletions"]["vector_memories"] == 5
        assert summary["estimated_deletions"]["history_entries"] == 10
        
    def test_get_reset_summary_vector_only(self, mock_stores):
        """Test getting reset summary for vector only"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        options = ResetOptions(scope=ResetScope.VECTOR_ONLY)
        summary = manager.get_reset_summary(options)
        
        assert "vector_store" in summary["components_to_reset"]
        assert "graph_store" not in summary["components_to_reset"]
        assert "history_database" not in summary["components_to_reset"]
        
    def test_reset_dry_run(self, mock_stores):
        """Test dry run doesn't execute any deletions"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        options = ResetOptions(dry_run=True)
        result = manager.reset(options)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "summary" in result
        
        # Verify no actual deletions
        vector_store.delete_col.assert_not_called()
        graph_store.graph.query.assert_not_called()
        db.connection.execute.assert_not_called()
        
    def test_reset_all_success(self, mock_stores):
        """Test successful full reset"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        options = ResetOptions(scope=ResetScope.ALL)
        result = manager.reset(options)
        
        assert result["success"] is True
        assert "vector_store" in result["components_reset"]
        assert "graph_store" in result["components_reset"]
        assert "history_database" in result["components_reset"]
        
        # Verify operations executed
        vector_store.delete_col.assert_called_once()
        graph_store.graph.query.assert_called_with(
            "\n        MATCH (n)\n        DETACH DELETE n\n        ",
            params={}
        )
        
    def test_reset_with_preserve_filters(self, mock_stores):
        """Test reset with preserve filters"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        # Setup preserved memories
        all_memories = [Mock(id=f"mem_{i}") for i in range(5)]
        preserve_memories = [all_memories[0], all_memories[2]]  # Preserve 2 memories
        
        vector_store.list.side_effect = [
            (all_memories,),  # First call returns all
            (preserve_memories,)  # Second call returns memories to preserve
        ]
        
        options = ResetOptions(
            scope=ResetScope.VECTOR_ONLY,
            preserve_filters={"user_id": "keep_user"}
        )
        result = manager.reset(options)
        
        assert result["success"] is True
        # Should delete 3 memories (5 total - 2 preserved)
        assert vector_store.delete.call_count == 3
        
    def test_reset_partial_failure(self, mock_stores):
        """Test reset with partial failure"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        # Make vector store fail
        vector_store.delete_col.side_effect = Exception("Vector store error")
        
        options = ResetOptions(scope=ResetScope.ALL)
        result = manager.reset(options)
        
        assert result["success"] is False
        assert "vector_store: Vector store error" in result["errors"]
        # Graph and history should still be attempted
        assert "graph_store" in result["components_reset"]
        assert "history_database" in result["components_reset"]
        
    def test_full_graph_reset(self, mock_stores):
        """Test full graph reset executes correct query"""
        vector_store, graph_store, db = mock_stores
        manager = ResetManager(vector_store, graph_store, db)
        
        manager._full_graph_reset()
        
        graph_store.graph.query.assert_called_with(
            "\n        MATCH (n)\n        DETACH DELETE n\n        ",
            params={}
        )


class TestAsyncResetManager:
    """Test AsyncResetManager functionality"""
    
    @pytest.mark.asyncio
    async def test_async_reset(self):
        """Test async reset operation"""
        vector_store = Mock()
        graph_store = Mock()
        db = Mock()
        
        vector_store.delete_col = Mock()
        graph_store.graph = Mock()
        graph_store.graph.query = Mock()
        db.connection = Mock()
        db.connection.execute = Mock()
        db._create_history_table = Mock()
        
        manager = AsyncResetManager(vector_store, graph_store, db)
        
        options = ResetOptions(scope=ResetScope.ALL)
        result = await manager.reset_async(options)
        
        assert result["success"] is True
        assert "vector_store" in result["components_reset"]
        assert "graph_store" in result["components_reset"]
        assert "history_database" in result["components_reset"]


def test_reset_scope_combinations():
    """Test all reset scope combinations are handled correctly"""
    test_cases = [
        # (keep_vector, keep_graph, keep_history, expected_scope)
        (False, False, False, ResetScope.ALL),
        (True, False, False, ResetScope.GRAPH_AND_HISTORY),
        (False, True, False, ResetScope.VECTOR_AND_HISTORY),
        (False, False, True, ResetScope.VECTOR_ONLY),
        (True, True, False, ResetScope.HISTORY_ONLY),
        (True, False, True, ResetScope.GRAPH_ONLY),
    ]
    
    for keep_vector, keep_graph, keep_history, expected_scope in test_cases:
        options = ResetOptions.from_cli_args(
            keep_vector=keep_vector,
            keep_graph=keep_graph,
            keep_history=keep_history
        )
        assert options.scope == expected_scope, (
            f"Failed for keep_vector={keep_vector}, "
            f"keep_graph={keep_graph}, keep_history={keep_history}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 