"""
SQLAlchemy models matching the Pascal database schema.
"""
import uuid
import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    SmallInteger,
    Boolean,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.config import get_settings

# Get embedding dimensions from config
# 768 for Gemini, 1536 for OpenAI
EMBEDDING_DIMENSIONS = get_settings().embedding_dimensions


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class MessageType(enum.Enum):
    """Message type enum."""
    human = "human"
    ai_assistant = "ai-assistant"


class Lead(Base):
    """Leads table model."""
    __tablename__ = "leads"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="lead", 
        cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="lead"
    )


class Project(Base):
    """Projects table model."""
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brochure_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    includes_parking: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    has_showroom: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Embedding for RAG (dimensions: 768 for Gemini, 1536 for OpenAI)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship(back_populates="project")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="most_recent_project")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="project")


class Typology(Base):
    """Typologies table model."""
    __tablename__ = "typologies"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    num_bedrooms: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    num_bathrooms: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    area_m2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship(back_populates="typology")


class Property(Base):
    """Properties table model."""
    __tablename__ = "properties"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pricing: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    view_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    floor_no: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True
    )
    typology_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("typologies.id"),
        nullable=True
    )
    
    # Embedding for RAG (dimensions: 768 for Gemini, 1536 for OpenAI)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship(back_populates="properties")
    typology: Mapped[Optional["Typology"]] = relationship(back_populates="properties")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="property")


class Conversation(Base):
    """Conversations table model."""
    __tablename__ = "conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    is_answered_by_lead: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Foreign keys
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("leads.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True
    )
    most_recent_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships
    lead: Mapped[Optional["Lead"]] = relationship(back_populates="conversations")
    most_recent_project: Mapped[Optional["Project"]] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", 
        cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="conversation")


class Message(Base):
    """Messages table model."""
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    type: Mapped[MessageType] = mapped_column(
        Enum(
            MessageType, 
            name="message_type", 
            create_type=False,
            values_callable=lambda e: [member.value for member in e]
        ),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Foreign keys
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Appointment(Base):
    """Appointments table model."""
    __tablename__ = "appointments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Foreign keys
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("leads.id"),
        nullable=True
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("conversations.id"),
        nullable=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id"),
        nullable=True
    )
    property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("properties.id"),
        nullable=True
    )
    
    # Relationships
    lead: Mapped[Optional["Lead"]] = relationship(back_populates="appointments")
    conversation: Mapped[Optional["Conversation"]] = relationship(back_populates="appointments")
    project: Mapped[Optional["Project"]] = relationship(back_populates="appointments")
    property: Mapped[Optional["Property"]] = relationship(back_populates="appointments")

