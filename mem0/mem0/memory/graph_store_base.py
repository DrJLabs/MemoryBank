import abc
from typing import List, Dict, Any

import logging

logger = logging.getLogger(__name__)


class GraphStoreBase(abc.ABC):
    """Provider-agnostic base for graph memory backends (Neo4j, Memgraph, etc.).

    Concrete subclasses are expected to supply:
      * A ``graph`` attribute exposing ``query`` for Cypher execution.
      * Provider-specific vector search / index creation logic inside their
        constructor or helper methods.
    The purpose of this base is to consolidate pure-Python helper methods that
    were duplicated across the provider implementations.
    """

    # ------------------------------------------------------------------
    # Shared helpers – identical in Neo4j and Memgraph variants previously
    # ------------------------------------------------------------------

    @staticmethod
    def _remove_spaces_from_entities(entity_list: List[Dict[str, Any]]):
        """Utility: normalise entity names to snake_case (was duplicated)."""
        cleaned = []
        for item in entity_list:
            cleaned.append(
                {
                    **item,
                    "source": item.get("source", "").lower().replace(" ", "_"),
                    "destination": item.get("destination", "").lower().replace(" ", "_"),
                }
            )
        return cleaned

    # Add further common helper functions here as we progressively extract them

    # ------------------------------------------------------------------
    # Abstract contract for subclasses
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def add(self, data, filters):
        """Add new entities/relationships parsed from *data* respecting *filters*."""

    @abc.abstractmethod
    def search(self, query, filters, limit=100):
        """Search graph relationships relevant to *query*."""

    @abc.abstractmethod
    def delete_all(self, filters):
        """Delete all graph data scoped by *filters*."""

    @abc.abstractmethod
    def get_all(self, filters, limit=100):
        """Return graph relationships for *filters* up to *limit*."""

    def __init__(self, config):
        """Store shared configuration reference for subclasses."""
        self.config = config