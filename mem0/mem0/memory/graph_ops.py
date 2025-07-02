import asyncio
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class GraphOperations:
    """Thin façade over the underlying graph store to isolate graph-specific logic.

    This helper reduces the size of the main Memory classes by providing a
    dedicated component responsible solely for graph interactions. Both
    synchronous and asynchronous callers can reuse the same interface—async
    contexts should call the `*_async` methods which internally delegate to a
    thread pool when necessary (because the underlying graph store is sync).
    """

    def __init__(self, graph_store, enabled: bool):
        self._graph = graph_store
        self._enabled = enabled and graph_store is not None

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def _ensure_user_filter(filters: Dict[str, Any]):
        """Graph queries require a user_id for proper partitioning."""
        if filters.get("user_id") is None:
            filters["user_id"] = "user"

    # ---------------------------------------------------------------------
    # Synchronous variants
    # ---------------------------------------------------------------------

    def add(self, messages: List[Dict[str, Any]], filters: Dict[str, Any]):
        if not self._enabled:
            return []
        self._ensure_user_filter(filters)
        data = "\n".join(
            [msg["content"] for msg in messages if msg.get("content") and msg.get("role") != "system"]
        )
        return self._graph.add(data, filters)

    def search(self, query: str, filters: Dict[str, Any], limit: int):
        if not self._enabled:
            return []
        self._ensure_user_filter(filters)
        return self._graph.search(query, filters, limit)

    def get_all(self, filters: Dict[str, Any], limit: int):
        if not self._enabled:
            return []
        self._ensure_user_filter(filters)
        return self._graph.get_all(filters, limit)

    def delete_all(self, filters: Dict[str, Any]):
        if not self._enabled:
            return
        self._ensure_user_filter(filters)
        self._graph.delete_all(filters)

    # ---------------------------------------------------------------------
    # Async wrappers (useful for AsyncMemory)
    # ---------------------------------------------------------------------

    async def add_async(self, messages: List[Dict[str, Any]], filters: Dict[str, Any]):
        return await asyncio.to_thread(self.add, messages, filters)

    async def search_async(self, query: str, filters: Dict[str, Any], limit: int):
        return await asyncio.to_thread(self.search, query, filters, limit)

    async def get_all_async(self, filters: Dict[str, Any], limit: int):
        return await asyncio.to_thread(self.get_all, filters, limit)

    async def delete_all_async(self, filters: Dict[str, Any]):
        await asyncio.to_thread(self.delete_all, filters)