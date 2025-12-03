"""
Conversation schemas.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from src.api.schemas.base import BaseSchema, TimestampMixin


class ConversationCreate(BaseSchema):
    """Schema for creating a conversation."""
    lead_id: UUID


class ConversationResponse(BaseSchema, TimestampMixin):
    """Schema for conversation response."""
    id: UUID
    lead_id: Optional[UUID] = None
    most_recent_project_id: Optional[UUID] = None
    last_message_at: Optional[datetime] = None
    is_answered_by_lead: Optional[bool] = False

