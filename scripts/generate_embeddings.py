"""
Script to generate embeddings for all properties and projects.
Run with: python -m scripts.generate_embeddings
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.database.connection import get_async_session, init_db
from src.database.repositories import ProjectRepository, PropertyRepository
from src.ai.embeddings import get_embedding_service


async def generate_project_embeddings(session):
    """Generate embeddings for all projects."""
    print("\n🏢 Generating project embeddings...")
    
    repo = ProjectRepository(session)
    embedding_service = get_embedding_service()
    
    projects = await repo.get_all()
    updated = 0
    
    for project in projects:
        if project.embedding:
            print(f"   ⏭️  {project.name} - already has embedding")
            continue
        
        # Create text representation
        project_data = {
            "name": project.name,
            "description": project.description,
            "district": project.district,
            "address": project.address,
            "reference": project.reference,
            "details": project.details,
            "includes_parking": project.includes_parking,
            "has_showroom": project.has_showroom,
        }
        text = embedding_service.create_project_text(project_data)
        
        # Generate embedding
        try:
            embedding = await embedding_service.generate(text)
            
            # Update project
            await repo.update_embedding(project.id, embedding)
            updated += 1
            print(f"   ✅ {project.name} - embedding generated ({len(embedding)} dimensions)")
        except Exception as e:
            print(f"   ❌ {project.name} - error: {e}")
    
    return updated


async def generate_property_embeddings(session):
    """Generate embeddings for all properties."""
    print("\n🏠 Generating property embeddings...")
    
    repo = PropertyRepository(session)
    embedding_service = get_embedding_service()
    
    properties = await repo.get_all_with_relations()
    updated = 0
    
    for prop in properties:
        if prop.embedding:
            print(f"   ⏭️  {prop.title} - already has embedding")
            continue
        
        # Create text representation
        property_data = {
            "title": prop.title,
            "description": prop.description,
            "project_name": prop.project.name if prop.project else None,
            "district": prop.project.district if prop.project else None,
            "num_bedrooms": prop.typology.num_bedrooms if prop.typology else None,
            "num_bathrooms": prop.typology.num_bathrooms if prop.typology else None,
            "pricing": prop.pricing,
            "view_type": prop.view_type,
            "area_m2": prop.typology.area_m2 if prop.typology else None,
        }
        text = embedding_service.create_property_text(property_data)
        
        # Generate embedding
        try:
            embedding = await embedding_service.generate(text)
            
            # Update property
            await repo.update_embedding(prop.id, embedding)
            updated += 1
            print(f"   ✅ {prop.title} - embedding generated")
        except Exception as e:
            print(f"   ❌ {prop.title} - error: {e}")
    
    return updated


async def verify_embeddings(session):
    """Verify that embeddings were generated correctly."""
    print("\n🔍 Verifying embeddings...")
    
    from sqlalchemy import text
    
    # Count properties with embeddings
    result = await session.execute(
        text("SELECT COUNT(*) FROM properties WHERE embedding IS NOT NULL")
    )
    props_with_embedding = result.scalar()
    
    result = await session.execute(
        text("SELECT COUNT(*) FROM properties")
    )
    total_props = result.scalar()
    
    # Count projects with embeddings
    result = await session.execute(
        text("SELECT COUNT(*) FROM projects WHERE embedding IS NOT NULL")
    )
    projects_with_embedding = result.scalar()
    
    result = await session.execute(
        text("SELECT COUNT(*) FROM projects")
    )
    total_projects = result.scalar()
    
    print(f"   Properties: {props_with_embedding}/{total_props} have embeddings")
    print(f"   Projects: {projects_with_embedding}/{total_projects} have embeddings")
    
    return props_with_embedding == total_props and projects_with_embedding == total_projects


async def main():
    """Main function."""
    settings = get_settings()
    
    print("=" * 50)
    print("🧠 Pascal Real Estate - Embedding Generator")
    print("=" * 50)
    print(f"\n📦 Provider: {settings.embedding_provider}")
    print(f"📐 Dimensions: {settings.embedding_dimensions}")
    print(f"🤖 Model: {settings.embedding_model}")
    
    # Validate API key
    if settings.embedding_provider == "gemini" and not settings.gemini_api_key:
        print("\n❌ Error: GEMINI_API_KEY not set in .env")
        return
    elif settings.embedding_provider == "openai" and not settings.openai_api_key:
        print("\n❌ Error: OPENAI_API_KEY not set in .env")
        return
    
    # Initialize database
    await init_db()
    
    async with get_async_session() as session:
        # Generate embeddings
        projects_updated = await generate_project_embeddings(session)
        properties_updated = await generate_property_embeddings(session)
        
        # Verify
        all_good = await verify_embeddings(session)
    
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    print(f"   Projects updated: {projects_updated}")
    print(f"   Properties updated: {properties_updated}")
    print(f"   Status: {'✅ All embeddings generated' if all_good else '⚠️ Some embeddings missing'}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
