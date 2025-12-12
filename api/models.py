import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Uuid, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    datasets = relationship("Dataset", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default="viewer")  # tenant_admin, analyst, viewer
    tenant_id = Column(Uuid(as_uuid=True), ForeignKey("tenants.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    meta_info = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=True)
    story = Column(Text, nullable=True)
    file_path = Column(String)  # MinIO path: tenants/{tenant_id}/{dataset_id}.csv
    tenant_id = Column(Uuid(as_uuid=True), ForeignKey("tenants.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="datasets")
