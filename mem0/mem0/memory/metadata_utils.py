from copy import deepcopy
from typing import Any, Dict, Optional, Tuple

__all__ = [
    "build_filters_and_metadata",
    "_build_filters_and_metadata",
]

def build_filters_and_metadata(
    *,  # Enforce keyword-only arguments
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    input_metadata: Optional[Dict[str, Any]] = None,
    input_filters: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Construct metadata for storage and filters for querying based on session and actor identifiers.

    This utility is shared by both the synchronous and asynchronous memory implementations.
    It scopes metadata and filters to the provided identifiers and resolves optional actor
    filtering. The behaviour is identical to the original inline helper in
    `mem0.memory.main` but extracted for reuse and testability.
    """

    base_metadata_template: Dict[str, Any] = deepcopy(input_metadata) if input_metadata else {}
    effective_query_filters: Dict[str, Any] = deepcopy(input_filters) if input_filters else {}

    # Track which session ids were provided to enforce requirement
    session_ids_provided = []

    if user_id:
        base_metadata_template["user_id"] = user_id
        effective_query_filters["user_id"] = user_id
        session_ids_provided.append("user_id")

    if agent_id:
        base_metadata_template["agent_id"] = agent_id
        effective_query_filters["agent_id"] = agent_id
        session_ids_provided.append("agent_id")

    if run_id:
        base_metadata_template["run_id"] = run_id
        effective_query_filters["run_id"] = run_id
        session_ids_provided.append("run_id")

    if not session_ids_provided:
        raise ValueError("At least one of 'user_id', 'agent_id', or 'run_id' must be provided.")

    # Optional actor filtering
    resolved_actor_id = actor_id or effective_query_filters.get("actor_id")
    if resolved_actor_id:
        effective_query_filters["actor_id"] = resolved_actor_id

    return base_metadata_template, effective_query_filters


# Backwards-compatibility alias used throughout the existing codebase
_build_filters_and_metadata = build_filters_and_metadata