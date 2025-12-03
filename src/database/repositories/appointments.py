"""
Appointment repository for database operations.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Appointment
from src.database.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """Repository for Appointment operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Appointment)
    
    async def get_by_id_with_relations(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Get appointment by ID with all relations loaded."""
        result = await self.session.execute(
            select(Appointment)
            .options(
                joinedload(Appointment.lead),
                joinedload(Appointment.project),
                joinedload(Appointment.property),
                joinedload(Appointment.conversation),
            )
            .where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_lead(self, lead_id: uuid.UUID) -> List[Appointment]:
        """Get all appointments for a lead."""
        result = await self.session.execute(
            select(Appointment)
            .options(
                joinedload(Appointment.project),
                joinedload(Appointment.property),
            )
            .where(Appointment.lead_id == lead_id)
            .order_by(Appointment.scheduled_for)
        )
        return list(result.scalars().all())
    
    async def get_by_project(self, project_id: uuid.UUID) -> List[Appointment]:
        """Get all appointments for a project."""
        result = await self.session.execute(
            select(Appointment)
            .options(joinedload(Appointment.lead))
            .where(Appointment.project_id == project_id)
            .order_by(Appointment.scheduled_for)
        )
        return list(result.scalars().all())
    
    async def get_upcoming(
        self,
        lead_id: Optional[uuid.UUID] = None,
        limit: int = 10,
    ) -> List[Appointment]:
        """Get upcoming appointments (scheduled_for > now)."""
        query = (
            select(Appointment)
            .options(
                joinedload(Appointment.lead),
                joinedload(Appointment.project),
            )
            .where(Appointment.scheduled_for > datetime.utcnow())
        )
        
        if lead_id:
            query = query.where(Appointment.lead_id == lead_id)
        
        query = query.order_by(Appointment.scheduled_for).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(
        self,
        lead_id: Optional[uuid.UUID] = None,
        conversation_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        property_id: Optional[uuid.UUID] = None,
        scheduled_for: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Appointment:
        """Create a new appointment."""
        appointment = Appointment(
            lead_id=lead_id,
            conversation_id=conversation_id,
            project_id=project_id,
            property_id=property_id,
            scheduled_for=scheduled_for,
            notes=notes,
        )
        self.session.add(appointment)
        await self.session.flush()
        return appointment
    
    async def check_availability(
        self,
        scheduled_for: datetime,
        project_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """
        Check if a time slot is available.
        Returns True if available, False if there's a conflict.
        """
        # Check for appointments within 1 hour of the requested time
        from datetime import timedelta
        
        start_window = scheduled_for - timedelta(hours=1)
        end_window = scheduled_for + timedelta(hours=1)
        
        query = select(Appointment).where(
            and_(
                Appointment.scheduled_for >= start_window,
                Appointment.scheduled_for <= end_window,
            )
        )
        
        if project_id:
            query = query.where(Appointment.project_id == project_id)
        
        result = await self.session.execute(query)
        existing = result.scalars().first()
        
        return existing is None

