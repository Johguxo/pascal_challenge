"""
Property routes.
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from src.api.schemas.properties import (
    PropertyCreate, 
    PropertyUpdate, 
    PropertyResponse,
    PropertySearchFilters,
)
from src.api.dependencies import get_db_session
from src.database.repositories import PropertyRepository

router = APIRouter()


def _property_to_response(prop) -> PropertyResponse:
    """Convert property model to response with nested data."""
    return PropertyResponse(
        id=prop.id,
        title=prop.title,
        type=prop.type,
        description=prop.description,
        pricing=prop.pricing,
        view_type=prop.view_type,
        floor_no=prop.floor_no,
        project_id=prop.project_id,
        typology_id=prop.typology_id,
        project_name=prop.project.name if prop.project else None,
        district=prop.project.district if prop.project else None,
        num_bedrooms=prop.typology.num_bedrooms if prop.typology else None,
        num_bathrooms=prop.typology.num_bathrooms if prop.typology else None,
        area_m2=prop.typology.area_m2 if prop.typology else None,
    )


@router.get("/", response_model=List[PropertyResponse])
async def list_properties(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all properties."""
    repo = PropertyRepository(session)
    properties = await repo.get_all_with_relations(skip=skip, limit=limit)
    return [_property_to_response(p) for p in properties]


@router.get("/search", response_model=List[PropertyResponse])
async def search_properties(
    district: Optional[str] = Query(None),
    num_bedrooms: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    project_id: Optional[UUID] = Query(None),
    limit: int = Query(10, le=50),
    session=Depends(get_db_session),
):
    """Search properties by filters."""
    repo = PropertyRepository(session)
    
    filters = {}
    if district:
        filters["district"] = district
    if num_bedrooms:
        filters["num_bedrooms"] = num_bedrooms
    if min_price:
        filters["min_price"] = min_price
    if max_price:
        filters["max_price"] = max_price
    if project_id:
        filters["project_id"] = project_id
    
    properties = await repo.search_by_filters(filters, limit=limit)
    return [_property_to_response(p) for p in properties]


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    session=Depends(get_db_session),
):
    """Get a property by ID."""
    repo = PropertyRepository(session)
    prop = await repo.get_by_id_with_relations(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return _property_to_response(prop)


@router.get("/project/{project_id}", response_model=List[PropertyResponse])
async def get_properties_by_project(
    project_id: UUID,
    session=Depends(get_db_session),
):
    """Get all properties for a project."""
    repo = PropertyRepository(session)
    properties = await repo.get_by_project(project_id)
    return [_property_to_response(p) for p in properties]


@router.post("/", response_model=PropertyResponse, status_code=201)
async def create_property(
    data: PropertyCreate,
    session=Depends(get_db_session),
):
    """Create a new property."""
    repo = PropertyRepository(session)
    prop = await repo.create(
        title=data.title,
        type=data.type,
        description=data.description,
        pricing=data.pricing,
        view_type=data.view_type,
        floor_no=data.floor_no,
        project_id=data.project_id,
        typology_id=data.typology_id,
    )
    # Fetch with relations for response
    prop_full = await repo.get_by_id_with_relations(prop.id)
    return _property_to_response(prop_full)


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    data: PropertyUpdate,
    session=Depends(get_db_session),
):
    """Update a property."""
    repo = PropertyRepository(session)
    prop = await repo.get_by_id(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    await repo.update(
        prop,
        title=data.title,
        type=data.type,
        description=data.description,
        pricing=data.pricing,
        view_type=data.view_type,
        floor_no=data.floor_no,
        project_id=data.project_id,
        typology_id=data.typology_id,
    )
    
    # Fetch with relations for response
    prop_full = await repo.get_by_id_with_relations(property_id)
    return _property_to_response(prop_full)


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: UUID,
    session=Depends(get_db_session),
):
    """Delete a property."""
    repo = PropertyRepository(session)
    deleted = await repo.delete_by_id(property_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Property not found")

