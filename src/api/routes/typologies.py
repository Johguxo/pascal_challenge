"""
Typology routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.typologies import TypologyCreate, TypologyUpdate, TypologyResponse
from src.api.dependencies import get_db_session
from src.database.repositories import TypologyRepository

router = APIRouter()


@router.get("/", response_model=List[TypologyResponse])
async def list_typologies(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all typologies."""
    repo = TypologyRepository(session)
    typologies = await repo.get_all(skip=skip, limit=limit)
    return typologies


@router.get("/{typology_id}", response_model=TypologyResponse)
async def get_typology(
    typology_id: UUID,
    session=Depends(get_db_session),
):
    """Get a typology by ID."""
    repo = TypologyRepository(session)
    typology = await repo.get_by_id(typology_id)
    if not typology:
        raise HTTPException(status_code=404, detail="Typology not found")
    return typology


@router.get("/bedrooms/{num_bedrooms}", response_model=List[TypologyResponse])
async def get_typologies_by_bedrooms(
    num_bedrooms: int,
    session=Depends(get_db_session),
):
    """Get typologies by number of bedrooms."""
    repo = TypologyRepository(session)
    typologies = await repo.get_by_bedrooms(num_bedrooms)
    return typologies


@router.post("/", response_model=TypologyResponse, status_code=201)
async def create_typology(
    data: TypologyCreate,
    session=Depends(get_db_session),
):
    """Create a new typology."""
    repo = TypologyRepository(session)
    typology = await repo.create(
        name=data.name,
        description=data.description,
        type=data.type,
        num_bedrooms=data.num_bedrooms,
        num_bathrooms=data.num_bathrooms,
        area_m2=data.area_m2,
    )
    return typology


@router.put("/{typology_id}", response_model=TypologyResponse)
async def update_typology(
    typology_id: UUID,
    data: TypologyUpdate,
    session=Depends(get_db_session),
):
    """Update a typology."""
    repo = TypologyRepository(session)
    typology = await repo.get_by_id(typology_id)
    if not typology:
        raise HTTPException(status_code=404, detail="Typology not found")
    
    updated = await repo.update(
        typology,
        name=data.name,
        description=data.description,
        type=data.type,
        num_bedrooms=data.num_bedrooms,
        num_bathrooms=data.num_bathrooms,
        area_m2=data.area_m2,
    )
    return updated


@router.delete("/{typology_id}", status_code=204)
async def delete_typology(
    typology_id: UUID,
    session=Depends(get_db_session),
):
    """Delete a typology."""
    repo = TypologyRepository(session)
    deleted = await repo.delete_by_id(typology_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Typology not found")

