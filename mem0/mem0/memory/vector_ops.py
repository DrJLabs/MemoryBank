import hashlib
import json
import logging
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz

from mem0.configs.base import MemoryItem, MemoryConfig
from mem0.configs.enums import MemoryType
from mem0.configs.prompts import get_update_memory_messages
from mem0.memory.utils import (
    get_fact_retrieval_messages,
    parse_messages,
    parse_vision_messages,
    process_telemetry_filters,
    remove_code_blocks,
)
from mem0.memory.telemetry import capture_event

logger = logging.getLogger(__name__)


class VectorStoreOperations:
    """Encapsulates all direct interactions with the vector store.

    This class is **synchronous**; an async counterpart is already covered by
    delegating to `asyncio.to_thread` within the `AsyncMemory` class or a future
    `AsyncVectorStoreOperations` implementation.
    """

    def __init__(
        self,
        *,
        embedding_model,
        vector_store,
        db,
        llm,
        config: MemoryConfig,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.db = db
        self.llm = llm
        self.config = config

    # ---------------------------------------------------------------------
    # Public helpers called by Memory
    # ---------------------------------------------------------------------

    def add(
        self,
        messages: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        query_filters_for_inference: Dict[str, Any],
        infer: bool,
    ) -> List[Dict[str, Any]]:
        """Add raw messages (or inferred facts) into the vector store."""
        if not infer:
            return self._add_raw_messages(messages, metadata)

        return self._add_with_inference(messages, metadata, query_filters_for_inference)

    # ------------------------------------------------------------------
    # Internal building blocks
    # ------------------------------------------------------------------

    def _add_raw_messages(self, messages: List[Dict[str, Any]], metadata: Dict[str, Any]):
        returned_memories: List[Dict[str, Any]] = []
        for message_dict in messages:
            if (
                not isinstance(message_dict, dict)
                or message_dict.get("role") is None
                or message_dict.get("content") is None
            ):
                logger.warning("Skipping invalid message format: %s", message_dict)
                continue

            if message_dict["role"] == "system":
                continue

            per_msg_meta = deepcopy(metadata)
            per_msg_meta["role"] = message_dict["role"]

            actor_name = message_dict.get("name")
            if actor_name:
                per_msg_meta["actor_id"] = actor_name

            msg_content = message_dict["content"]
            msg_embeddings = self.embedding_model.embed(msg_content, "add")
            mem_id = self._create_memory(msg_content, msg_embeddings, per_msg_meta)

            returned_memories.append(
                {
                    "id": mem_id,
                    "memory": msg_content,
                    "event": "ADD",
                    "actor_id": actor_name if actor_name else None,
                    "role": message_dict["role"],
                }
            )
        return returned_memories

    # ------------------------------------------------------------------
    def _add_with_inference(
        self,
        messages: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """LLM-assisted add procedure (fact extraction & update/delete)."""
        if self.config.llm.config.get("enable_vision"):
            messages = parse_vision_messages(messages, self.llm, self.config.llm.config.get("vision_details"))
        else:
            messages = parse_vision_messages(messages)

        parsed_messages = parse_messages(messages)

        if self.config.custom_fact_extraction_prompt:
            system_prompt = self.config.custom_fact_extraction_prompt
            user_prompt = f"Input:\n{parsed_messages}"
        else:
            system_prompt, user_prompt = get_fact_retrieval_messages(parsed_messages)

        response = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        try:
            response = remove_code_blocks(response)
            new_retrieved_facts = json.loads(response)["facts"]
        except Exception as e:  # noqa: BLE001
            logger.error("Error parsing LLM facts: %s", e)
            new_retrieved_facts = []

        if not new_retrieved_facts:
            logger.debug("No new facts retrieved – skipping memory update LLM call.")

        retrieved_old_memory: List[Dict[str, str]] = []
        new_message_embeddings: Dict[str, Any] = {}
        for new_mem in new_retrieved_facts:
            messages_embeddings = self.embedding_model.embed(new_mem, "add")
            new_message_embeddings[new_mem] = messages_embeddings
            existing_memories = self.vector_store.search(
                query=new_mem,
                vectors=messages_embeddings,
                limit=5,
                filters=filters,
            )
            for mem in existing_memories:
                retrieved_old_memory.append({"id": mem.id, "text": mem.payload["data"]})

        # Deduplicate on id
        unique_data: Dict[str, Dict[str, str]] = {item["id"]: item for item in retrieved_old_memory}
        retrieved_old_memory = list(unique_data.values())
        logger.info("Total existing memories: %s", len(retrieved_old_memory))

        # Map UUIDs to integers to avoid hallucinations
        temp_uuid_mapping: Dict[str, str] = {}
        for idx, item in enumerate(retrieved_old_memory):
            temp_uuid_mapping[str(idx)] = item["id"]
            retrieved_old_memory[idx]["id"] = str(idx)

        if new_retrieved_facts:
            function_calling_prompt = get_update_memory_messages(
                retrieved_old_memory, new_retrieved_facts, self.config.custom_update_memory_prompt
            )
            try:
                response: str = self.llm.generate_response(
                    messages=[{"role": "user", "content": function_calling_prompt}],
                    response_format={"type": "json_object"},
                )
            except Exception as e:  # noqa: BLE001
                logger.error("Error in new memory actions response: %s", e)
                response = ""
            try:
                response = remove_code_blocks(response)
                new_memories_with_actions = json.loads(response)
            except Exception as e:  # noqa: BLE001
                logger.error("Invalid JSON response: %s", e)
                new_memories_with_actions = {}
        else:
            new_memories_with_actions = {}

        returned_memories: List[Dict[str, Any]] = []
        try:
            for resp in new_memories_with_actions.get("memory", []):
                logger.debug("Memory action: %s", resp)
                try:
                    action_text = resp.get("text")
                    if not action_text:
                        logger.debug("Skipping memory entry due to empty text field.")
                        continue

                    event_type = resp.get("event")
                    if event_type == "ADD":
                        memory_id = self._create_memory(
                            data=action_text,
                            existing_embeddings=new_message_embeddings,
                            metadata=deepcopy(metadata),
                        )
                        returned_memories.append({"id": memory_id, "memory": action_text, "event": event_type})
                    elif event_type == "UPDATE":
                        self._update_memory(
                            memory_id=temp_uuid_mapping[resp.get("id")],
                            data=action_text,
                            existing_embeddings=new_message_embeddings,
                            metadata=deepcopy(metadata),
                        )
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": action_text,
                                "event": event_type,
                                "previous_memory": resp.get("old_memory"),
                            }
                        )
                    elif event_type == "DELETE":
                        self._delete_memory(memory_id=temp_uuid_mapping[resp.get("id")])
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": action_text,
                                "event": event_type,
                            }
                        )
                    elif event_type == "NONE":
                        logger.debug("NOOP for Memory.")
                except Exception as e:  # noqa: BLE001
                    logger.error("Error processing memory action: %s", e)
        except Exception as e:  # noqa: BLE001
            logger.error("Error in memory processing loop: %s", e)

        keys, encoded_ids = process_telemetry_filters(filters)
        capture_event(
            "mem0.add",
            self,
            {"version": self.config.version, "keys": keys, "encoded_ids": encoded_ids, "sync_type": "sync"},
        )
        return returned_memories

    # ------------------------------------------------------------------
    def _create_memory(self, data: str, existing_embeddings: Dict[str, Any], metadata=None):
        logger.debug("Creating memory with data=%s", data)
        if data in existing_embeddings:
            embeddings = existing_embeddings[data]
        else:
            embeddings = self.embedding_model.embed(data, memory_action="add")

        memory_id = str(uuid.uuid4())
        metadata = metadata or {}
        metadata["data"] = data
        metadata["hash"] = hashlib.md5(data.encode()).hexdigest()
        metadata["created_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()

        self.vector_store.insert(vectors=[embeddings], ids=[memory_id], payloads=[metadata])

        self.db.add_history(
            memory_id,
            None,
            data,
            "ADD",
            created_at=metadata.get("created_at"),
            actor_id=metadata.get("actor_id"),
            role=metadata.get("role"),
        )

        capture_event("mem0._create_memory", self, {"memory_id": memory_id, "sync_type": "sync"})
        return memory_id

    # ------------------------------------------------------------------
    def _update_memory(
        self,
        memory_id: str,
        data: str,
        existing_embeddings: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        logger.info("Updating memory %s", memory_id)
        existing_memory = self.vector_store.get(vector_id=memory_id)
        if not existing_memory:
            raise ValueError(f"Memory with id {memory_id} not found")

        prev_value = existing_memory.payload.get("data")
        new_metadata = deepcopy(metadata) if metadata is not None else {}

        new_metadata["data"] = data
        new_metadata["hash"] = hashlib.md5(data.encode()).hexdigest()
        new_metadata["created_at"] = existing_memory.payload.get("created_at")
        new_metadata["updated_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()

        for key in ("user_id", "agent_id", "run_id", "actor_id", "role"):
            if key in existing_memory.payload:
                new_metadata[key] = existing_memory.payload[key]

        if data in existing_embeddings:
            embeddings = existing_embeddings[data]
        else:
            embeddings = self.embedding_model.embed(data, "update")

        self.vector_store.update(vector_id=memory_id, vector=embeddings, payload=new_metadata)
        self.db.add_history(
            memory_id,
            prev_value,
            data,
            "UPDATE",
            created_at=new_metadata["created_at"],
            updated_at=new_metadata["updated_at"],
            actor_id=new_metadata.get("actor_id"),
            role=new_metadata.get("role"),
        )
        capture_event("mem0._update_memory", self, {"memory_id": memory_id, "sync_type": "sync"})
        return memory_id

    # ------------------------------------------------------------------
    def _delete_memory(self, memory_id: str):
        logger.info("Deleting memory %s", memory_id)
        existing_memory = self.vector_store.get(vector_id=memory_id)
        prev_value = existing_memory.payload["data"]

        self.vector_store.delete(vector_id=memory_id)
        self.db.add_history(
            memory_id,
            prev_value,
            None,
            "DELETE",
            actor_id=existing_memory.payload.get("actor_id"),
            role=existing_memory.payload.get("role"),
            is_deleted=1,
        )
        capture_event("mem0._delete_memory", self, {"memory_id": memory_id, "sync_type": "sync"})
        return memory_id

    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        embeddings = self.embedding_model.embed(query, "search")
        memories = self.vector_store.search(query=query, vectors=embeddings, limit=limit, filters=filters)

        promoted_payload_keys = [
            "user_id",
            "agent_id",
            "run_id",
            "actor_id",
            "role",
        ]
        core_and_promoted_keys = {
            "data",
            "hash",
            "created_at",
            "updated_at",
            "id",
            *promoted_payload_keys,
        }

        original_memories: List[Dict[str, Any]] = []
        for mem in memories:
            mem_dict = MemoryItem(
                id=mem.id,
                memory=mem.payload["data"],
                hash=mem.payload.get("hash"),
                created_at=mem.payload.get("created_at"),
                updated_at=mem.payload.get("updated_at"),
                score=mem.score,
            ).model_dump()

            for key in promoted_payload_keys:
                if key in mem.payload:
                    mem_dict[key] = mem.payload[key]

            additional_metadata = {k: v for k, v in mem.payload.items() if k not in core_and_promoted_keys}
            if additional_metadata:
                mem_dict["metadata"] = additional_metadata

            if threshold is None or mem.score >= threshold:
                original_memories.append(mem_dict)

        return original_memories

    # ------------------------------------------------------------------
    def get_all(self, filters: Dict[str, Any], limit: int):
        memories_result = self.vector_store.list(filters=filters, limit=limit)
        actual_memories = (
            memories_result[0] if isinstance(memories_result, (tuple, list)) and len(memories_result) > 0 else memories_result
        )

        promoted_payload_keys = [
            "user_id",
            "agent_id",
            "run_id",
            "actor_id",
            "role",
        ]
        core_and_promoted_keys = {
            "data",
            "hash",
            "created_at",
            "updated_at",
            "id",
            *promoted_payload_keys,
        }

        formatted_memories: List[Dict[str, Any]] = []
        for mem in actual_memories:
            mem_dict = MemoryItem(
                id=mem.id,
                memory=mem.payload["data"],
                hash=mem.payload.get("hash"),
                created_at=mem.payload.get("created_at"),
                updated_at=mem.payload.get("updated_at"),
            ).model_dump(exclude={"score"})

            for key in promoted_payload_keys:
                if key in mem.payload:
                    mem_dict[key] = mem.payload[key]

            additional_metadata = {k: v for k, v in mem.payload.items() if k not in core_and_promoted_keys}
            if additional_metadata:
                mem_dict["metadata"] = additional_metadata

            formatted_memories.append(mem_dict)

        return formatted_memories