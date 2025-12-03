"""
Project repository for database operations.
"""
import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Project
from src.database.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
    
    async def get_by_id_with_properties(self, project_id: uuid.UUID) -> Optional[Project]:
        """Get project by ID with its properties loaded."""
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.properties))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name (case-insensitive partial match)."""
        result = await self.session.execute(
            select(Project).where(Project.name.ilike(f"%{name}%"))
        )
        return result.scalar_one_or_none()
    
    async def get_by_district(self, district: str) -> List[Project]:
        """Get all projects in a district."""
        result = await self.session.execute(
            select(Project).where(Project.district.ilike(f"%{district}%"))
        )
        return list(result.scalars().all())
    
    async def get_all_with_properties(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with their properties."""
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.properties))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        district: Optional[str] = None,
        address: Optional[str] = None,
        reference: Optional[str] = None,
        details: Optional[str] = None,
        video_url: Optional[str] = None,
        brochure_url: Optional[str] = None,
        includes_parking: bool = False,
        has_showroom: bool = False,
        embedding: Optional[List[float]] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            description=description,
            district=district,
            address=address,
            reference=reference,
            details=details,
            video_url=video_url,
            brochure_url=brochure_url,
            includes_parking=includes_parking,
            has_showroom=has_showroom,
            embedding=embedding,
        )
        self.session.add(project)
        await self.session.flush()
        return project
    
    async def update_embedding(self, project_id: uuid.UUID, embedding: List[float]) -> Optional[Project]:
        """Update project embedding."""
        project = await self.get_by_id(project_id)
        if project:
            project.embedding = embedding
            await self.session.flush()
        return project
    
    async def search_by_embedding(
        self,
        query_embedding: List[float],
        limit: int = 5,
    ) -> List[Project]:
        """Search projects by embedding similarity."""
        result = await self.session.execute(
            select(Project)
            .where(Project.embedding.isnot(None))
            .order_by(Project.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        return list(result.scalars().all())

