"""
Script to migrate embedding columns when changing providers.
Run with: python -m scripts.migrate_embeddings

This script:
1. Drops existing embedding columns
2. Recreates them with the new dimensions
3. You'll need to regenerate embeddings after running this

WARNING: This will delete all existing embeddings!
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.config import get_settings
from src.database.connection import async_engine


async def migrate_embeddings():
    """Migrate embedding columns to new dimensions."""
    settings = get_settings()
    dimensions = settings.embedding_dimensions
    
    print("=" * 50)
    print("🔄 Pascal Real Estate - Embedding Migration")
    print("=" * 50)
    print(f"\n📐 Target dimensions: {dimensions}")
    print(f"📦 Provider: {settings.embedding_provider}")
    
    # Confirm
    print("\n⚠️  WARNING: This will delete all existing embeddings!")
    confirm = input("Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("❌ Migration cancelled.")
        return
    
    async with async_engine.begin() as conn:
        print("\n🔄 Migrating projects.embedding column...")
        
        # Drop and recreate projects.embedding
        await conn.execute(text("ALTER TABLE projects DROP COLUMN IF EXISTS embedding"))
        await conn.execute(text(f"ALTER TABLE projects ADD COLUMN embedding vector({dimensions})"))
        print("   ✅ projects.embedding migrated")
        
        print("\n🔄 Migrating properties.embedding column...")
        
        # Drop and recreate properties.embedding
        await conn.execute(text("ALTER TABLE properties DROP COLUMN IF EXISTS embedding"))
        await conn.execute(text(f"ALTER TABLE properties ADD COLUMN embedding vector({dimensions})"))
        print("   ✅ properties.embedding migrated")
        
        # Create index for similarity search
        print("\n🔄 Creating vector indexes...")
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_projects_embedding 
            ON projects USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        print("   ✅ projects embedding index created")
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_embedding 
            ON properties USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        print("   ✅ properties embedding index created")
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed!")
    print("=" * 50)
    print("\n📝 Next steps:")
    print("   1. Run: python -m scripts.generate_embeddings")
    print("   2. Restart the API server")


if __name__ == "__main__":
    asyncio.run(migrate_embeddings())

