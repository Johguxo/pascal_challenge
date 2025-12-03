"""
Appointment schemas.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional

from src.api.schemas.base import BaseSchema, TimestampMixin


class AppointmentBase(BaseSchema):
    """Base appointment schema."""
    lead_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    scheduled_for: Optional[datetime] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment."""
    scheduled_for: datetime  # Required


class AppointmentUpdate(BaseSchema):
    """Schema for updating an appointment."""
    scheduled_for: Optional[datetime] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase, TimestampMixin):
    """Schema for appointment response."""
    id: UUID
    # Nested data (optional)
    project_name: Optional[str] = None
    lead_name: Optional[str] = None

