"""
Seed script to populate the database with test data.
Run with: python -m scripts.seed_data
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.database.connection import get_async_session, init_db
from src.database.repositories import (
    ProjectRepository,
    PropertyRepository,
    TypologyRepository,
    LeadRepository,
)


# Data directory
DATA_DIR = Path(__file__).parent / "data"


def load_json(filename: str) -> list:
    """Load JSON data from file."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_typologies(session) -> dict:
    """Seed typologies and return mapping of name -> id."""
    print("\n📋 Seeding typologies...")
    
    repo = TypologyRepository(session)
    data = load_json("typologies.json")
    
    typology_map = {}
    
    for item in data:
        # Check if exists
        existing = await repo.get_by_name(item["name"])
        if existing:
            print(f"   ⏭️  Typology '{item['name']}' already exists")
            typology_map[item["name"]] = existing.id
            continue
        
        typology = await repo.create(
            name=item["name"],
            description=item["description"],
            type=item["type"],
            num_bedrooms=item["num_bedrooms"],
            num_bathrooms=item["num_bathrooms"],
            area_m2=item["area_m2"],
        )
        typology_map[item["name"]] = typology.id
        print(f"   ✅ Created typology: {item['name']}")
    
    return typology_map


async def seed_projects(session) -> dict:
    """Seed projects and return mapping of name -> id."""
    print("\n🏢 Seeding projects...")
    
    repo = ProjectRepository(session)
    data = load_json("projects.json")
    
    project_map = {}
    
    for item in data:
        # Check if exists
        existing = await repo.get_by_name(item["name"])
        if existing:
            print(f"   ⏭️  Project '{item['name']}' already exists")
            project_map[item["name"]] = existing.id
            continue
        
        project = await repo.create(
            name=item["name"],
            description=item["description"],
            district=item["district"],
            address=item["address"],
            reference=item["reference"],
            details=item["details"],
            video_url=item.get("video_url"),
            brochure_url=item.get("brochure_url"),
            includes_parking=item.get("includes_parking", False),
            has_showroom=item.get("has_showroom", False),
        )
        project_map[item["name"]] = project.id
        print(f"   ✅ Created project: {item['name']} ({item['district']})")
    
    return project_map


async def seed_properties(session, project_map: dict, typology_map: dict) -> int:
    """Seed properties using project and typology mappings."""
    print("\n🏠 Seeding properties...")
    
    repo = PropertyRepository(session)
    data = load_json("properties.json")
    
    created_count = 0
    
    for item in data:
        project_id = project_map.get(item["project_name"])
        typology_id = typology_map.get(item["typology_name"])
        
        if not project_id:
            print(f"   ⚠️  Project '{item['project_name']}' not found, skipping")
            continue
        
        if not typology_id:
            print(f"   ⚠️  Typology '{item['typology_name']}' not found, skipping")
            continue
        
        # Check if property with same title exists
        existing_props = await repo.get_by_project(project_id)
        if any(p.title == item["title"] for p in existing_props):
            print(f"   ⏭️  Property '{item['title']}' already exists")
            continue
        
        await repo.create(
            title=item["title"],
            type=item["type"],
            description=item["description"],
            pricing=item["pricing"],
            view_type=item["view_type"],
            floor_no=item["floor_no"],
            project_id=project_id,
            typology_id=typology_id,
        )
        created_count += 1
        price_formatted = f"${item['pricing']:,}"
        print(f"   ✅ Created: {item['title']} - {price_formatted}")
    
    return created_count


async def seed_test_lead(session) -> None:
    """Create a test lead."""
    print("\n👤 Creating test lead...")
    
    repo = LeadRepository(session)
    
    # Check if test lead exists
    existing = await repo.get_by_telegram_chat_id("test_chat_123")
    if existing:
        print("   ⏭️  Test lead already exists")
        return
    
    await repo.create(
        telegram_chat_id="test_chat_123",
        name="Usuario de Prueba",
        email="test@pascal.pe",
        phone="+51 999 888 777",
    )
    print("   ✅ Created test lead: Usuario de Prueba")


async def print_summary(session) -> None:
    """Print database summary."""
    print("\n" + "=" * 50)
    print("📊 Database Summary")
    print("=" * 50)
    
    from src.database.repositories import (
        LeadRepository,
        ProjectRepository,
        PropertyRepository,
        TypologyRepository,
        AppointmentRepository,
    )
    
    lead_repo = LeadRepository(session)
    project_repo = ProjectRepository(session)
    property_repo = PropertyRepository(session)
    typology_repo = TypologyRepository(session)
    
    leads = await lead_repo.count()
    projects = await project_repo.count()
    properties = await property_repo.count()
    typologies = await typology_repo.count()
    
    print(f"   Leads:      {leads}")
    print(f"   Projects:   {projects}")
    print(f"   Properties: {properties}")
    print(f"   Typologies: {typologies}")
    
    # Show properties by district
    print("\n📍 Properties by District:")
    all_projects = await project_repo.get_all()
    for project in all_projects:
        props = await property_repo.get_by_project(project.id)
        if props:
            total_value = sum(p.pricing or 0 for p in props)
            print(f"   {project.district}: {len(props)} properties (${total_value:,})")


async def main():
    """Main seed function."""
    print("=" * 50)
    print("🌱 Pascal Real Estate - Database Seeder")
    print("=" * 50)
    
    # Initialize database
    print("\n🔄 Initializing database...")
    await init_db()
    print("   ✅ Database ready")
    
    async with get_async_session() as session:
        # Seed in order (respecting foreign keys)
        typology_map = await seed_typologies(session)
        project_map = await seed_projects(session)
        properties_created = await seed_properties(session, project_map, typology_map)
        await seed_test_lead(session)
        
        # Print summary
        await print_summary(session)
    
    print("\n" + "=" * 50)
    print("🎉 Seeding completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

