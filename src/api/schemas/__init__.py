"""
Pydantic schemas for API request/response validation.
"""
from src.api.schemas.base import BaseSchema, TimestampMixin
from src.api.schemas.leads import LeadCreate, LeadUpdate, LeadResponse
from src.api.schemas.conversations import ConversationCreate, ConversationResponse
from src.api.schemas.messages import MessageCreate, MessageResponse
from src.api.schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from src.api.schemas.properties import PropertyCreate, PropertyUpdate, PropertyResponse, PropertySearchFilters
from src.api.schemas.typologies import TypologyCreate, TypologyUpdate, TypologyResponse
from src.api.schemas.appointments import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from src.api.schemas.chat import ChatRequest, ChatResponse, PropertyItem

__all__ = [
    # Base
    "BaseSchema",
    "TimestampMixin",
    # Leads
    "LeadCreate",
    "LeadUpdate", 
    "LeadResponse",
    # Conversations
    "ConversationCreate",
    "ConversationResponse",
    # Messages
    "MessageCreate",
    "MessageResponse",
    # Projects
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Properties
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyResponse",
    "PropertySearchFilters",
    # Typologies
    "TypologyCreate",
    "TypologyUpdate",
    "TypologyResponse",
    # Appointments
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "PropertyItem",
]

