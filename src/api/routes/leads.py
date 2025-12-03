"""
Lead routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.leads import LeadCreate, LeadUpdate, LeadResponse
from src.api.dependencies import get_db_session
from src.database.repositories import LeadRepository

router = APIRouter()


@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all leads."""
    repo = LeadRepository(session)
    leads = await repo.get_all(skip=skip, limit=limit)
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    session=Depends(get_db_session),
):
    """Get a lead by ID."""
    repo = LeadRepository(session)
    lead = await repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/telegram/{chat_id}", response_model=LeadResponse)
async def get_lead_by_telegram(
    chat_id: str,
    session=Depends(get_db_session),
):
    """Get a lead by Telegram chat ID."""
    repo = LeadRepository(session)
    lead = await repo.get_by_telegram_chat_id(chat_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(
    data: LeadCreate,
    session=Depends(get_db_session),
):
    """Create a new lead."""
    repo = LeadRepository(session)
    lead = await repo.create(
        telegram_chat_id=data.telegram_chat_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
    )
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    session=Depends(get_db_session),
):
    """Update a lead."""
    repo = LeadRepository(session)
    lead = await repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    updated = await repo.update(
        lead,
        name=data.name,
        email=data.email,
        phone=data.phone,
        telegram_chat_id=data.telegram_chat_id,
    )
    return updated


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: UUID,
    session=Depends(get_db_session),
):
    """Delete a lead."""
    repo = LeadRepository(session)
    deleted = await repo.delete_by_id(lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")

