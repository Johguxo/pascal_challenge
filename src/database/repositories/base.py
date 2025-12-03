"""
Base repository with common CRUD operations.
"""
import uuid
from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        """Get entity by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count total entities."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
    
    async def create(self, **kwargs) -> T:
        """Create a new entity."""
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        return entity
    
    async def update(self, entity: T, **kwargs) -> T:
        """Update entity fields."""
        for key, value in kwargs.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        await self.session.flush()
        return entity
    
    async def delete(self, entity: T) -> None:
        """Delete an entity."""
        await self.session.delete(entity)
        await self.session.flush()
    
    async def delete_by_id(self, entity_id: uuid.UUID) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.delete(entity)
            return True
        return False

