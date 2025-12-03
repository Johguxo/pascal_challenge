"""
Project schemas.
"""
from uuid import UUID
from typing import Optional

from src.api.schemas.base import BaseSchema


class ProjectBase(BaseSchema):
    """Base project schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    reference: Optional[str] = None
    details: Optional[str] = None
    video_url: Optional[str] = None
    brochure_url: Optional[str] = None
    includes_parking: Optional[bool] = False
    has_showroom: Optional[bool] = False


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    name: str  # Required


class ProjectUpdate(ProjectBase):
    """Schema for updating a project."""
    pass


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: UUID

