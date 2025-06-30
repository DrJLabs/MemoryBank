from app.workers.celery_app import celery_app
import time
from app.core.database import SessionLocal
from app import models
from app.models.custom_gpt import OperationType
import uuid

@celery_app.task
def log_search_activity(application_id: str, request_data: dict, response_status: int, request_id: str):
    """
    Logs the search activity to the audit log.
    """
    db = SessionLocal()
    try:
        audit_log_entry = models.CustomGPTAuditLog(
            id=uuid.uuid4(),
            application_id=application_id,
            operation_type=OperationType.search,
            request_data=request_data,
            response_status=response_status,
            memory_service_request_id=request_id,
        )
        db.add(audit_log_entry)
        db.commit()
    finally:
        db.close()

@celery_app.task(bind=True, queue="memory_creation")
async def log_memory_creation_activity(self, application_id: str, request_data: dict, request_id: str):
    """
    Logs the memory creation request and forwards it to the Memory Bank Service.
    """
    db = SessionLocal()
    try:
        # 1. Log the initial "pending" state
        audit_log_entry = models.CustomGPTAuditLog(
            id=uuid.uuid4(),
            application_id=application_id,
            operation_type=OperationType.create,
            request_data=request_data,
            response_status=202, # Accepted
            memory_service_request_id=request_id,
        )
        db.add(audit_log_entry)
        db.commit()
        db.refresh(audit_log_entry)

        # 2. Call the Memory Bank Service
        from app.clients.memory_bank_client import memory_bank_client
        memory_content = request_data.get("content")
        memory_context = request_data.get("context", {})
        
        # Add source tracking
        memory_context['source'] = 'custom-gpt'
        memory_context['application_id'] = application_id

        creation_response = await memory_bank_client.create_memory(
            content=memory_content,
            metadata=memory_context
        )

        # 3. Update the audit log with the final status
        audit_log_entry.response_status = creation_response.get("status_code", 201)
        audit_log_entry.memory_service_response = creation_response
        db.commit()

    except Exception as e:
        # 4. Log failure state
        if 'audit_log_entry' in locals() and db.object_session(audit_log_entry):
            audit_log_entry.response_status = 500
            audit_log_entry.memory_service_response = {"error": str(e)}
            db.commit()
    finally:
        db.close()

@celery_app.task(bind=True)
def process_memory_task(self, data: dict):
    """
    Placeholder task for processing memory.
    This task simulates some work and returns a result.
    """
    print(f"Task {self.request.id}: Processing memory with data: {data}")
    time.sleep(5)  # Simulate a 5-second task
    result = {"status": "processed", "data": data, "task_id": self.request.id}
    print(f"Task {self.request.id}: Finished processing.")
    return result 