"""
Typology repository for database operations.
"""
import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Typology
from src.database.repositories.base import BaseRepository


class TypologyRepository(BaseRepository[Typology]):
    """Repository for Typology operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Typology)
    
    async def get_by_bedrooms(self, num_bedrooms: int) -> List[Typology]:
        """Get all typologies with specified number of bedrooms."""
        result = await self.session.execute(
            select(Typology).where(Typology.num_bedrooms == num_bedrooms)
        )
        return list(result.scalars().all())
    
    async def get_by_type(self, type_name: str) -> Optional[Typology]:
        """Get typology by type name."""
        result = await self.session.execute(
            select(Typology).where(Typology.type == type_name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Typology]:
        """Get typology by name."""
        result = await self.session.execute(
            select(Typology).where(Typology.name.ilike(f"%{name}%"))
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        num_bedrooms: Optional[int] = None,
        num_bathrooms: Optional[int] = None,
        area_m2: Optional[str] = None,
    ) -> Typology:
        """Create a new typology."""
        typology = Typology(
            name=name,
            description=description,
            type=type,
            num_bedrooms=num_bedrooms,
            num_bathrooms=num_bathrooms,
            area_m2=area_m2,
        )
        self.session.add(typology)
        await self.session.flush()
        return typology

