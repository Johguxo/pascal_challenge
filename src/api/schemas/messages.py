"""
Message schemas.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

from src.api.schemas.base import BaseSchema


class MessageTypeEnum(str, Enum):
    """Message type enum for API."""
    human = "human"
    ai_assistant = "ai-assistant"


class MessageCreate(BaseSchema):
    """Schema for creating a message."""
    conversation_id: UUID
    content: str
    type: MessageTypeEnum


class MessageResponse(BaseSchema):
    """Schema for message response."""
    id: UUID
    conversation_id: UUID
    content: str
    type: MessageTypeEnum
    created_at: Optional[datetime] = None

