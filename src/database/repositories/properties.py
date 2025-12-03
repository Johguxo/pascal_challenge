"""
Property repository for database operations.
"""
import uuid
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Property, Project, Typology
from src.database.repositories.base import BaseRepository


class PropertyRepository(BaseRepository[Property]):
    """Repository for Property operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Property)
    
    async def get_by_id_with_relations(self, property_id: uuid.UUID) -> Optional[Property]:
        """Get property by ID with project and typology loaded."""
        result = await self.session.execute(
            select(Property)
            .options(
                joinedload(Property.project),
                joinedload(Property.typology),
            )
            .where(Property.id == property_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_project(self, project_id: uuid.UUID) -> List[Property]:
        """Get all properties for a project."""
        result = await self.session.execute(
            select(Property)
            .options(joinedload(Property.typology))
            .where(Property.project_id == project_id)
        )
        return list(result.scalars().all())
    
    async def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Property]:
        """Get all properties with project and typology."""
        result = await self.session.execute(
            select(Property)
            .options(
                joinedload(Property.project),
                joinedload(Property.typology),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().unique().all())
    
    async def create(
        self,
        title: Optional[str] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        pricing: Optional[int] = None,
        view_type: Optional[str] = None,
        floor_no: Optional[str] = None,
        project_id: Optional[uuid.UUID] = None,
        typology_id: Optional[uuid.UUID] = None,
        embedding: Optional[List[float]] = None,
    ) -> Property:
        """Create a new property."""
        property = Property(
            title=title,
            type=type,
            description=description,
            pricing=pricing,
            view_type=view_type,
            floor_no=floor_no,
            project_id=project_id,
            typology_id=typology_id,
            embedding=embedding,
        )
        self.session.add(property)
        await self.session.flush()
        return property
    
    async def update_embedding(self, property_id: uuid.UUID, embedding: List[float]) -> Optional[Property]:
        """Update property embedding."""
        property = await self.get_by_id(property_id)
        if property:
            property.embedding = embedding
            await self.session.flush()
        return property
    
    async def search_by_embedding(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[dict] = None,
    ) -> List[Property]:
        """
        Search properties by embedding similarity with optional filters.
        
        Filters can include:
        - max_price: int
        - min_price: int
        - num_bedrooms: int
        - district: str
        - project_id: uuid.UUID
        """
        query = (
            select(Property)
            .options(
                joinedload(Property.project),
                joinedload(Property.typology),
            )
            .where(Property.embedding.isnot(None))
        )
        
        # Apply filters
        if filters:
            conditions = []
            
            if filters.get("max_price"):
                conditions.append(Property.pricing <= filters["max_price"])
            
            if filters.get("min_price"):
                conditions.append(Property.pricing >= filters["min_price"])
            
            if filters.get("project_id"):
                conditions.append(Property.project_id == filters["project_id"])
            
            if filters.get("num_bedrooms"):
                query = query.join(Property.typology)
                conditions.append(Typology.num_bedrooms == filters["num_bedrooms"])
            
            if filters.get("district"):
                query = query.join(Property.project)
                conditions.append(Project.district.ilike(f"%{filters['district']}%"))
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by similarity and limit
        query = query.order_by(
            Property.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().unique().all())
    
    async def search_by_filters(
        self,
        filters: dict,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Property]:
        """Search properties by filters without embedding."""
        query = (
            select(Property)
            .options(
                joinedload(Property.project),
                joinedload(Property.typology),
            )
        )
        
        conditions = []
        
        if filters.get("max_price"):
            conditions.append(Property.pricing <= filters["max_price"])
        
        if filters.get("min_price"):
            conditions.append(Property.pricing >= filters["min_price"])
        
        if filters.get("project_id"):
            conditions.append(Property.project_id == filters["project_id"])
        
        if filters.get("num_bedrooms"):
            query = query.join(Property.typology)
            conditions.append(Typology.num_bedrooms == filters["num_bedrooms"])
        
        if filters.get("district"):
            query = query.join(Property.project)
            conditions.append(Project.district.ilike(f"%{filters['district']}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().unique().all())

