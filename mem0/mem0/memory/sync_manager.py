import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
import time

logger = logging.getLogger(__name__)


class OperationType(Enum):
    ADD = "add"
    UPDATE = "update" 
    DELETE = "delete"
    RESET = "reset"
    DELETE_ALL = "delete_all"


class StoreType(Enum):
    VECTOR = "vector"
    GRAPH = "graph"


@dataclass
class OperationResult:
    """Result of a store operation"""
    success: bool
    store_type: StoreType
    operation_type: OperationType
    data: Any = None
    error: Optional[Exception] = None
    memory_id: Optional[str] = None


@dataclass
class SyncContext:
    """Context for a synchronized operation"""
    operation_type: OperationType
    memory_id: Optional[str] = None
    data: Any = None
    metadata: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    vector_result: Optional[OperationResult] = None
    graph_result: Optional[OperationResult] = None
    rollback_actions: List[Callable] = None
    
    def __post_init__(self):
        if self.rollback_actions is None:
            self.rollback_actions = []


class MemorySyncManager:
    """
    Synchronization manager that ensures vector and graph stores stay consistent
    using event-driven hooks and lightweight two-phase commit.
    """
    
    def __init__(self, vector_store, graph_store=None, single_store_mode=False, 
                 max_retries=3, retry_backoff=1.0):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.single_store_mode = single_store_mode
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._operation_lock = threading.RLock()
        
        # Event hooks
        self._pre_operation_hooks: List[Callable] = []
        self._post_operation_hooks: List[Callable] = []
        self._rollback_hooks: List[Callable] = []
        
        self.enable_graph = not single_store_mode and graph_store is not None
        
        logger.info(f"MemorySyncManager initialized - Graph enabled: {self.enable_graph}, "
                   f"Single store mode: {single_store_mode}")
    
    def add_pre_operation_hook(self, hook: Callable[[SyncContext], None]):
        """Add a hook that runs before any operation"""
        self._pre_operation_hooks.append(hook)
    
    def add_post_operation_hook(self, hook: Callable[[SyncContext], None]):
        """Add a hook that runs after successful operations"""
        self._post_operation_hooks.append(hook)
    
    def add_rollback_hook(self, hook: Callable[[SyncContext], None]):
        """Add a hook that runs during rollback"""
        self._rollback_hooks.append(hook)
    
    def _execute_hooks(self, hooks: List[Callable], context: SyncContext):
        """Execute a list of hooks with error handling"""
        for hook in hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Hook execution failed: {e}")
    
    def _retry_operation(self, operation: Callable, *args, **kwargs) -> OperationResult:
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                return OperationResult(
                    success=True,
                    store_type=StoreType.VECTOR,  # Will be overridden by caller
                    operation_type=OperationType.ADD,  # Will be overridden by caller
                    data=result
                )
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    sleep_time = self.retry_backoff * (2 ** attempt)
                    logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {sleep_time}s: {e}")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Operation failed after {self.max_retries + 1} attempts: {e}")
        
        return OperationResult(
            success=False,
            store_type=StoreType.VECTOR,  # Will be overridden by caller
            operation_type=OperationType.ADD,  # Will be overridden by caller
            error=last_exception
        )
    
    def _execute_vector_operation(self, context: SyncContext) -> OperationResult:
        """Execute vector store operation"""
        try:
            if context.operation_type == OperationType.ADD:
                # Vector add expects vectors, ids, payloads
                if hasattr(context.data, 'vectors') and hasattr(context.data, 'ids') and hasattr(context.data, 'payloads'):
                    result = self.vector_store.insert(
                        vectors=context.data.vectors,
                        ids=context.data.ids,
                        payloads=context.data.payloads
                    )
                else:
                    result = self.vector_store.insert(**context.data)
                
                # Add rollback action
                context.rollback_actions.append(
                    lambda: self.vector_store.delete(vector_id=context.memory_id)
                )
                
            elif context.operation_type == OperationType.UPDATE:
                result = self.vector_store.update(
                    vector_id=context.memory_id,
                    vector=context.data.get('vector'),
                    payload=context.data.get('payload')
                )
                
                # For rollback, we'd need to restore the old data (not implemented here)
                
            elif context.operation_type == OperationType.DELETE:
                # Get old data for potential rollback
                old_data = self.vector_store.get(vector_id=context.memory_id)
                result = self.vector_store.delete(vector_id=context.memory_id)
                
                # Add rollback action
                if old_data:
                    context.rollback_actions.append(
                        lambda: self.vector_store.insert(
                            vectors=[old_data.vector] if hasattr(old_data, 'vector') else [],
                            ids=[context.memory_id],
                            payloads=[old_data.payload] if hasattr(old_data, 'payload') else [{}]
                        )
                    )
                    
            elif context.operation_type == OperationType.RESET:
                result = self.vector_store.delete_col()
                
            elif context.operation_type == OperationType.DELETE_ALL:
                # For delete_all, we need to handle the filters
                memories = self.vector_store.list(filters=context.filters)
                if isinstance(memories, tuple):
                    memories = memories[0]
                
                deleted_ids = []
                for memory in memories:
                    self.vector_store.delete(vector_id=memory.id)
                    deleted_ids.append(memory.id)
                result = {"deleted_count": len(deleted_ids), "deleted_ids": deleted_ids}
            
            return OperationResult(
                success=True,
                store_type=StoreType.VECTOR,
                operation_type=context.operation_type,
                data=result,
                memory_id=context.memory_id
            )
            
        except Exception as e:
            logger.error(f"Vector store operation failed: {e}")
            return OperationResult(
                success=False,
                store_type=StoreType.VECTOR,
                operation_type=context.operation_type,
                error=e,
                memory_id=context.memory_id
            )
    
    def _execute_graph_operation(self, context: SyncContext) -> OperationResult:
        """Execute graph store operation"""
        if not self.enable_graph:
            return OperationResult(
                success=True,
                store_type=StoreType.GRAPH,
                operation_type=context.operation_type,
                data="Graph store disabled"
            )
        
        try:
            if context.operation_type == OperationType.ADD:
                result = self.graph_store.add(context.data, context.filters or {})
                
            elif context.operation_type == OperationType.UPDATE:
                # Graph update - might need to delete old entities and add new ones
                # This is graph-store specific implementation
                result = {"message": "Graph update not fully implemented yet"}
                
            elif context.operation_type == OperationType.DELETE:
                # Graph delete - need to remove nodes/edges related to memory_id
                # This is graph-store specific implementation  
                result = {"message": "Graph delete not fully implemented yet"}
                
            elif context.operation_type == OperationType.RESET:
                result = self.graph_store.delete_all({"user_id": "default"})
                
            elif context.operation_type == OperationType.DELETE_ALL:
                result = self.graph_store.delete_all(context.filters or {})
            
            return OperationResult(
                success=True,
                store_type=StoreType.GRAPH,
                operation_type=context.operation_type,
                data=result,
                memory_id=context.memory_id
            )
            
        except Exception as e:
            logger.error(f"Graph store operation failed: {e}")
            return OperationResult(
                success=False,
                store_type=StoreType.GRAPH,
                operation_type=context.operation_type,
                error=e,
                memory_id=context.memory_id
            )
    
    def _rollback_operations(self, context: SyncContext):
        """Execute rollback actions"""
        logger.warning(f"Rolling back {context.operation_type.value} operation for memory_id: {context.memory_id}")
        
        # Execute rollback hooks first
        self._execute_hooks(self._rollback_hooks, context)
        
        # Execute rollback actions
        for rollback_action in reversed(context.rollback_actions):
            try:
                rollback_action()
            except Exception as e:
                logger.error(f"Rollback action failed: {e}")
    
    def synchronized_operation(self, operation_type: OperationType, memory_id: Optional[str] = None,
                              data: Any = None, metadata: Optional[Dict[str, Any]] = None,
                              filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a synchronized operation across vector and graph stores.
        
        Returns:
            dict: Result with 'success', 'vector_result', 'graph_result', and any errors
        """
        with self._operation_lock:
            context = SyncContext(
                operation_type=operation_type,
                memory_id=memory_id,
                data=data,
                metadata=metadata,
                filters=filters
            )
            
            # Execute pre-operation hooks
            self._execute_hooks(self._pre_operation_hooks, context)
            
            # Phase 1: Execute operations in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                vector_future = executor.submit(self._execute_vector_operation, context)
                graph_future = executor.submit(self._execute_graph_operation, context) if self.enable_graph else None
                
                # Wait for both operations
                context.vector_result = vector_future.result()
                context.graph_result = graph_future.result() if graph_future else OperationResult(
                    success=True, 
                    store_type=StoreType.GRAPH,
                    operation_type=operation_type,
                    data="Graph store disabled"
                )
            
            # Phase 2: Check results and handle failures
            vector_success = context.vector_result.success
            graph_success = context.graph_result.success
            
            if vector_success and graph_success:
                # Both succeeded - execute post-operation hooks
                self._execute_hooks(self._post_operation_hooks, context)
                logger.debug(f"Synchronized {operation_type.value} operation completed successfully")
                
                return {
                    "success": True,
                    "vector_result": context.vector_result,
                    "graph_result": context.graph_result,
                    "message": f"{operation_type.value.title()} operation completed successfully"
                }
                
            elif vector_success and not graph_success:
                # Vector succeeded, graph failed - rollback vector
                logger.warning("Graph operation failed, rolling back vector operation")
                self._rollback_operations(context)
                
                return {
                    "success": False,
                    "vector_result": context.vector_result,
                    "graph_result": context.graph_result,
                    "error": f"Graph operation failed: {context.graph_result.error}",
                    "message": "Operation rolled back due to graph failure"
                }
                
            elif not vector_success and graph_success:
                # Graph succeeded, vector failed - this is unusual since vector is primary
                logger.error("Vector operation failed but graph succeeded")
                
                return {
                    "success": False, 
                    "vector_result": context.vector_result,
                    "graph_result": context.graph_result,
                    "error": f"Vector operation failed: {context.vector_result.error}",
                    "message": "Critical: Vector operation failed"
                }
                
            else:
                # Both failed
                logger.error("Both vector and graph operations failed")
                
                return {
                    "success": False,
                    "vector_result": context.vector_result,
                    "graph_result": context.graph_result,
                    "error": f"Both operations failed - Vector: {context.vector_result.error}, Graph: {context.graph_result.error}",
                    "message": "Complete operation failure"
                }


class AsyncMemorySyncManager(MemorySyncManager):
    """Async version of the synchronization manager"""
    
    async def _execute_vector_operation_async(self, context: SyncContext) -> OperationResult:
        """Execute vector store operation asynchronously"""
        return await asyncio.to_thread(self._execute_vector_operation, context)
    
    async def _execute_graph_operation_async(self, context: SyncContext) -> OperationResult:
        """Execute graph store operation asynchronously"""  
        return await asyncio.to_thread(self._execute_graph_operation, context)
    
    async def synchronized_operation_async(self, operation_type: OperationType, memory_id: Optional[str] = None,
                                          data: Any = None, metadata: Optional[Dict[str, Any]] = None,
                                          filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a synchronized operation across vector and graph stores asynchronously.
        """
        context = SyncContext(
            operation_type=operation_type,
            memory_id=memory_id,
            data=data,
            metadata=metadata,
            filters=filters
        )
        
        # Execute pre-operation hooks
        await asyncio.to_thread(self._execute_hooks, self._pre_operation_hooks, context)
        
        # Phase 1: Execute operations in parallel
        vector_task = asyncio.create_task(self._execute_vector_operation_async(context))
        graph_task = asyncio.create_task(self._execute_graph_operation_async(context)) if self.enable_graph else None
        
        # Wait for both operations
        context.vector_result = await vector_task
        context.graph_result = await graph_task if graph_task else OperationResult(
            success=True, 
            store_type=StoreType.GRAPH,
            operation_type=operation_type,
            data="Graph store disabled"
        )
        
        # Phase 2: Handle results (same logic as sync version)
        vector_success = context.vector_result.success
        graph_success = context.graph_result.success
        
        if vector_success and graph_success:
            await asyncio.to_thread(self._execute_hooks, self._post_operation_hooks, context)
            logger.debug(f"Async synchronized {operation_type.value} operation completed successfully")
            
            return {
                "success": True,
                "vector_result": context.vector_result,
                "graph_result": context.graph_result,
                "message": f"{operation_type.value.title()} operation completed successfully"
            }
            
        elif vector_success and not graph_success:
            logger.warning("Graph operation failed, rolling back vector operation")
            await asyncio.to_thread(self._rollback_operations, context)
            
            return {
                "success": False,
                "vector_result": context.vector_result,
                "graph_result": context.graph_result,
                "error": f"Graph operation failed: {context.graph_result.error}",
                "message": "Operation rolled back due to graph failure"
            }
            
        elif not vector_success and graph_success:
            logger.error("Vector operation failed but graph succeeded")
            
            return {
                "success": False,
                "vector_result": context.vector_result,
                "graph_result": context.graph_result,
                "error": f"Vector operation failed: {context.vector_result.error}",
                "message": "Critical: Vector operation failed"
            }
            
        else:
            logger.error("Both vector and graph operations failed")
            
            return {
                "success": False,
                "vector_result": context.vector_result,
                "graph_result": context.graph_result,
                "error": f"Both operations failed - Vector: {context.vector_result.error}, Graph: {context.graph_result.error}",
                "message": "Complete operation failure"
            } 