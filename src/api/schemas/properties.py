"""
Property schemas.
"""
from uuid import UUID
from typing import Optional

from src.api.schemas.base import BaseSchema


class PropertyBase(BaseSchema):
    """Base property schema."""
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    pricing: Optional[int] = None
    view_type: Optional[str] = None
    floor_no: Optional[str] = None
    project_id: Optional[UUID] = None
    typology_id: Optional[UUID] = None


class PropertyCreate(PropertyBase):
    """Schema for creating a property."""
    title: str  # Required


class PropertyUpdate(PropertyBase):
    """Schema for updating a property."""
    pass


class PropertyResponse(PropertyBase):
    """Schema for property response."""
    id: UUID
    # Nested data (optional, populated when needed)
    project_name: Optional[str] = None
    district: Optional[str] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    area_m2: Optional[str] = None


class PropertySearchFilters(BaseSchema):
    """Schema for property search filters."""
    query: Optional[str] = None
    district: Optional[str] = None
    num_bedrooms: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    project_id: Optional[UUID] = None
    limit: int = 10

