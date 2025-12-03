"""
Chat schemas for the main conversational endpoint.
"""
from uuid import UUID
from typing import Optional, List, Literal
from datetime import datetime

from src.api.schemas.base import BaseSchema


class ChatRequest(BaseSchema):
    """Schema for chat request."""
    message: str
    session_id: Optional[str] = None  # For web frontend
    channel: Literal["web", "telegram", "whatsapp"] = "web"
    channel_user_id: Optional[str] = None  # telegram_chat_id, whatsapp_id, etc.
    user_name: Optional[str] = None


class PropertyItem(BaseSchema):
    """Schema for property item in chat response."""
    id: UUID
    title: Optional[str] = None
    project_name: Optional[str] = None
    price_usd: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    district: Optional[str] = None
    floor: Optional[str] = None
    area_m2: Optional[str] = None


class AppointmentInfo(BaseSchema):
    """Schema for appointment info in chat response."""
    id: UUID
    scheduled_for: Optional[datetime] = None
    project_name: Optional[str] = None
    property_title: Optional[str] = None


class ChatDebugInfo(BaseSchema):
    """Debug information for development."""
    intent: Optional[str] = None
    rag_results_count: Optional[int] = None
    cached: bool = False
    processing_time_ms: Optional[int] = None


class ChatResponse(BaseSchema):
    """Schema for chat response."""
    type: Literal[
        "ONBOARDING",
        "PROPERTY_SEARCH_RESULT", 
        "SCHEDULE_CONFIRMATION",
        "SCHEDULE_REQUEST",
        "ERROR",
    ]
    response: str  # The main text response for the user
    summary: Optional[str] = None
    properties: Optional[List[PropertyItem]] = None
    appointment: Optional[AppointmentInfo] = None
    suggested_actions: Optional[List[str]] = None
    conversation_id: Optional[UUID] = None
    debug: Optional[ChatDebugInfo] = None

