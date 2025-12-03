"""
RAG Search Service for semantic property and project search.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.embeddings import get_embedding_service
from src.database.repositories import PropertyRepository, ProjectRepository
from src.cache import SearchCache, get_redis_client


class RAGSearchService:
    """
    Service for semantic search using RAG (Retrieval-Augmented Generation).
    Uses embeddings + pgvector for similarity search.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embedding_service = get_embedding_service()
        self.property_repo = PropertyRepository(session)
        self.project_repo = ProjectRepository(session)
        self.search_cache = SearchCache(get_redis_client())
    
    async def search_properties(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search properties using semantic similarity.
        
        Args:
            query: Natural language search query
            filters: Optional filters (num_bedrooms, district, max_price, etc.)
            limit: Maximum number of results
            use_cache: Whether to use cached results
        
        Returns:
            List of property dictionaries with relevance
        """
        # Check cache
        if use_cache:
            cached = await self.search_cache.get(query, filters)
            if cached:
                return cached
        
        # Generate embedding for query
        query_embedding = await self.embedding_service.generate(query)
        
        # Search using pgvector
        properties = await self.property_repo.search_by_embedding(
            query_embedding=query_embedding,
            limit=limit,
            filters=filters,
        )
        
        # Convert to dict format
        results = []
        for prop in properties:
            results.append({
                "id": str(prop.id),
                "title": prop.title,
                "type": prop.type,
                "description": prop.description,
                "price_usd": prop.pricing,
                "view_type": prop.view_type,
                "floor": prop.floor_no,
                "project_id": str(prop.project_id) if prop.project_id else None,
                "project_name": prop.project.name if prop.project else None,
                "district": prop.project.district if prop.project else None,
                "bedrooms": prop.typology.num_bedrooms if prop.typology else None,
                "bathrooms": prop.typology.num_bathrooms if prop.typology else None,
                "area_m2": prop.typology.area_m2 if prop.typology else None,
            })
        
        # Cache results
        if use_cache and results:
            await self.search_cache.set(query, results, filters)
        
        return results
    
    async def search_projects(
        self,
        query: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Search projects using semantic similarity.
        """
        query_embedding = await self.embedding_service.generate(query)
        
        projects = await self.project_repo.search_by_embedding(
            query_embedding=query_embedding,
            limit=limit,
        )
        
        results = []
        for proj in projects:
            results.append({
                "id": str(proj.id),
                "name": proj.name,
                "description": proj.description,
                "district": proj.district,
                "address": proj.address,
                "reference": proj.reference,
                "includes_parking": proj.includes_parking,
                "has_showroom": proj.has_showroom,
            })
        
        return results
    
    async def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get project by name (partial match)."""
        project = await self.project_repo.get_by_name(name)
        if not project:
            return None
        
        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "district": project.district,
            "address": project.address,
            "reference": project.reference,
            "details": project.details,
            "includes_parking": project.includes_parking,
            "has_showroom": project.has_showroom,
        }
    
    async def get_properties_for_project(
        self,
        project_id: UUID,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get all properties for a specific project."""
        properties = await self.property_repo.get_by_project(project_id)
        
        results = []
        for prop in properties[:limit]:
            results.append({
                "id": str(prop.id),
                "title": prop.title,
                "type": prop.type,
                "description": prop.description,
                "price_usd": prop.pricing,
                "view_type": prop.view_type,
                "floor": prop.floor_no,
                "bedrooms": prop.typology.num_bedrooms if prop.typology else None,
                "bathrooms": prop.typology.num_bathrooms if prop.typology else None,
                "area_m2": prop.typology.area_m2 if prop.typology else None,
            })
        
        return results

