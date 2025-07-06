import uuid
import enum
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class OperationType(enum.Enum):
    search = "search"
    create = "create"
    authenticate = "authenticate"

class CustomGPTApplication(Base):
    __tablename__ = "custom_gpt_applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    client_id = Column(String, unique=True, index=True, nullable=False)
    client_secret = Column(String, nullable=False)
    permissions = Column(JSON, default=[])
    rate_limit = Column(String, default="10/minute")
    rate_limits = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used = Column(DateTime, onupdate=datetime.datetime.utcnow)
    
    sessions = relationship("CustomGPTSession", back_populates="application")
    audit_logs = relationship("CustomGPTAuditLog", back_populates="application")

class CustomGPTSession(Base):
    __tablename__ = "custom_gpt_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("custom_gpt_applications.id"), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("CustomGPTApplication", back_populates="sessions")

class CustomGPTAuditLog(Base):
    __tablename__ = "custom_gpt_audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("custom_gpt_applications.id"), nullable=False)
    operation_type = Column(Enum(OperationType))
    request_data = Column(JSON)
    response_status = Column(Integer)
    processing_time = Column(Float)
    memory_service_request_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("CustomGPTApplication", back_populates="audit_logs") 