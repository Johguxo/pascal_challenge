"""
Lead repository for database operations.
"""
import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Lead
from src.database.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """Repository for Lead operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Lead)
    
    async def get_by_id(self, lead_id: uuid.UUID) -> Optional[Lead]:
        """Get lead by ID."""
        result = await self.session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_telegram_chat_id(self, chat_id: str) -> Optional[Lead]:
        """Get lead by Telegram chat ID."""
        result = await self.session.execute(
            select(Lead).where(Lead.telegram_chat_id == chat_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self, 
        telegram_chat_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Lead:
        """Create a new lead."""
        lead = Lead(
            telegram_chat_id=telegram_chat_id,
            name=name,
            email=email,
            phone=phone,
        )
        self.session.add(lead)
        await self.session.flush()
        return lead
    
    async def get_or_create_by_telegram_chat_id(
        self, 
        chat_id: str,
        name: Optional[str] = None,
    ) -> tuple[Lead, bool]:
        """Get existing lead or create new one. Returns (lead, created)."""
        existing = await self.get_by_telegram_chat_id(chat_id)
        if existing:
            return existing, False
        
        new_lead = await self.create(telegram_chat_id=chat_id, name=name)
        return new_lead, True
    
    async def update(self, lead: Lead, **kwargs) -> Lead:
        """Update lead fields."""
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        await self.session.flush()
        return lead

