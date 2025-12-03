"""
Appointment routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.appointments import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse,
)
from src.api.dependencies import get_db_session
from src.database.repositories import AppointmentRepository

router = APIRouter()


def _appointment_to_response(apt) -> AppointmentResponse:
    """Convert appointment model to response with nested data."""
    return AppointmentResponse(
        id=apt.id,
        lead_id=apt.lead_id,
        conversation_id=apt.conversation_id,
        project_id=apt.project_id,
        property_id=apt.property_id,
        scheduled_for=apt.scheduled_for,
        notes=apt.notes,
        created_at=apt.created_at,
        project_name=apt.project.name if apt.project else None,
        lead_name=apt.lead.name if apt.lead else None,
    )


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all appointments."""
    repo = AppointmentRepository(session)
    appointments = await repo.get_all(skip=skip, limit=limit)
    return appointments


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    limit: int = 10,
    session=Depends(get_db_session),
):
    """Get upcoming appointments."""
    repo = AppointmentRepository(session)
    appointments = await repo.get_upcoming(limit=limit)
    return [_appointment_to_response(a) for a in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    session=Depends(get_db_session),
):
    """Get an appointment by ID."""
    repo = AppointmentRepository(session)
    appointment = await repo.get_by_id_with_relations(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _appointment_to_response(appointment)


@router.get("/lead/{lead_id}", response_model=List[AppointmentResponse])
async def get_appointments_by_lead(
    lead_id: UUID,
    session=Depends(get_db_session),
):
    """Get all appointments for a lead."""
    repo = AppointmentRepository(session)
    appointments = await repo.get_by_lead(lead_id)
    return [_appointment_to_response(a) for a in appointments]


@router.get("/project/{project_id}", response_model=List[AppointmentResponse])
async def get_appointments_by_project(
    project_id: UUID,
    session=Depends(get_db_session),
):
    """Get all appointments for a project."""
    repo = AppointmentRepository(session)
    appointments = await repo.get_by_project(project_id)
    return [_appointment_to_response(a) for a in appointments]


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    session=Depends(get_db_session),
):
    """Create a new appointment."""
    repo = AppointmentRepository(session)
    
    # Check availability
    is_available = await repo.check_availability(
        data.scheduled_for, 
        data.project_id
    )
    if not is_available:
        raise HTTPException(
            status_code=409, 
            detail="Time slot not available"
        )
    
    appointment = await repo.create(
        lead_id=data.lead_id,
        conversation_id=data.conversation_id,
        project_id=data.project_id,
        property_id=data.property_id,
        scheduled_for=data.scheduled_for,
        notes=data.notes,
    )
    
    # Fetch with relations
    apt_full = await repo.get_by_id_with_relations(appointment.id)
    return _appointment_to_response(apt_full)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    session=Depends(get_db_session),
):
    """Update an appointment."""
    repo = AppointmentRepository(session)
    appointment = await repo.get_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check availability if rescheduling
    if data.scheduled_for and data.scheduled_for != appointment.scheduled_for:
        is_available = await repo.check_availability(
            data.scheduled_for,
            appointment.project_id
        )
        if not is_available:
            raise HTTPException(
                status_code=409,
                detail="Time slot not available"
            )
    
    await repo.update(
        appointment,
        scheduled_for=data.scheduled_for,
        notes=data.notes,
    )
    
    # Fetch with relations
    apt_full = await repo.get_by_id_with_relations(appointment_id)
    return _appointment_to_response(apt_full)


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: UUID,
    session=Depends(get_db_session),
):
    """Delete an appointment."""
    repo = AppointmentRepository(session)
    deleted = await repo.delete_by_id(appointment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Appointment not found")

