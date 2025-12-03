"""
Embedding service - Uses configured provider for generating embeddings.
"""
from typing import List, Optional
from functools import lru_cache

from src.ai.providers import get_embedding_provider, BaseEmbeddingProvider


class EmbeddingService:
    """Service for generating text embeddings using configured provider."""
    
    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None):
        self.provider = provider or get_embedding_provider()
    
    @property
    def dimensions(self) -> int:
        """Get the embedding dimensions for the current provider."""
        return self.provider.dimensions
    
    @property
    def provider_name(self) -> str:
        """Get the current provider name."""
        return self.provider.provider_name
    
    async def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return await self.provider.generate(text)
    
    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return await self.provider.generate_batch(texts)
    
    def create_property_text(self, property_data: dict) -> str:
        """
        Create a text representation of a property for embedding.
        Combines relevant fields into a searchable text.
        """
        parts = []
        
        if property_data.get("title"):
            parts.append(property_data["title"])
        
        if property_data.get("description"):
            parts.append(property_data["description"])
        
        if property_data.get("project_name"):
            parts.append(f"Proyecto: {property_data['project_name']}")
        
        if property_data.get("district"):
            parts.append(f"Ubicación: {property_data['district']}")
        
        if property_data.get("num_bedrooms") is not None:
            parts.append(f"{property_data['num_bedrooms']} dormitorios")
        
        if property_data.get("num_bathrooms") is not None:
            parts.append(f"{property_data['num_bathrooms']} baños")
        
        if property_data.get("pricing"):
            parts.append(f"Precio: ${property_data['pricing']:,}")
        
        if property_data.get("view_type"):
            parts.append(f"Vista: {property_data['view_type']}")
        
        if property_data.get("area_m2"):
            parts.append(f"Área: {property_data['area_m2']} m²")
        
        return ". ".join(parts)
    
    def create_project_text(self, project_data: dict) -> str:
        """
        Create a text representation of a project for embedding.
        """
        parts = []
        
        if project_data.get("name"):
            parts.append(f"Proyecto {project_data['name']}")
        
        if project_data.get("description"):
            parts.append(project_data["description"])
        
        if project_data.get("district"):
            parts.append(f"Ubicado en {project_data['district']}")
        
        if project_data.get("address"):
            parts.append(f"Dirección: {project_data['address']}")
        
        if project_data.get("reference"):
            parts.append(f"Referencia: {project_data['reference']}")
        
        if project_data.get("details"):
            parts.append(project_data["details"])
        
        features = []
        if project_data.get("includes_parking"):
            features.append("incluye estacionamiento")
        if project_data.get("has_showroom"):
            features.append("tiene showroom disponible")
        
        if features:
            parts.append("Características: " + ", ".join(features))
        
        return ". ".join(parts)


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
