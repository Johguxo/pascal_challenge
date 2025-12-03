"""
Lead schemas.
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr

from src.api.schemas.base import BaseSchema, TimestampMixin


class LeadBase(BaseModel):
    """Base lead schema."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead."""
    pass


class LeadUpdate(LeadBase):
    """Schema for updating a lead."""
    pass


class LeadResponse(BaseSchema, LeadBase, TimestampMixin):
    """Schema for lead response."""
    id: UUID

