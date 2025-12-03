"""
Typology schemas.
"""
from uuid import UUID
from typing import Optional

from src.api.schemas.base import BaseSchema


class TypologyBase(BaseSchema):
    """Base typology schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    area_m2: Optional[str] = None


class TypologyCreate(TypologyBase):
    """Schema for creating a typology."""
    name: str  # Required


class TypologyUpdate(TypologyBase):
    """Schema for updating a typology."""
    pass


class TypologyResponse(TypologyBase):
    """Schema for typology response."""
    id: UUID

