"""
Test script to verify all database and cache connections.
Run with: python -m scripts.test_connections
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_postgres_connection():
    """Test PostgreSQL connection."""
    print("\n🐘 Testing PostgreSQL connection...")
    
    try:
        from sqlalchemy import text
        from src.database.connection import async_engine
        
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✅ Connected to PostgreSQL")
            print(f"   📌 Version: {version[:50]}...")
            
            # Check pgvector extension
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            has_vector = result.scalar()
            if has_vector:
                print("   ✅ pgvector extension is installed")
            else:
                print("   ⚠️  pgvector extension not found")
            
            return True
    except Exception as e:
        print(f"   ❌ PostgreSQL connection failed: {e}")
        return False


async def test_redis_connection():
    """Test Redis connection."""
    print("\n🔴 Testing Redis connection...")
    
    try:
        from src.cache.redis_client import get_redis_client
        
        redis = get_redis_client()
        is_connected = await redis.ping()
        
        if is_connected:
            print("   ✅ Connected to Redis")
            
            # Test basic operations
            await redis.set("test_key", "test_value", ttl_seconds=10)
            value = await redis.get("test_key")
            
            if value == "test_value":
                print("   ✅ Redis read/write working")
            else:
                print("   ⚠️  Redis read/write issue")
            
            await redis.delete("test_key")
            return True
        else:
            print("   ❌ Redis ping failed")
            return False
    except Exception as e:
        print(f"   ❌ Redis connection failed: {e}")
        return False


async def test_database_tables():
    """Test that database tables exist."""
    print("\n📊 Testing database tables...")
    
    try:
        from src.database.connection import async_engine, init_db
        from sqlalchemy import text
        
        # Initialize tables
        print("   🔄 Creating tables if not exist...")
        await init_db()
        print("   ✅ Tables initialized")
        
        # Check tables
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'leads', 'conversations', 'messages',
                'projects', 'properties', 'typologies', 'appointments'
            ]
            
            print(f"   📋 Found tables: {', '.join(tables)}")
            
            missing = set(expected_tables) - set(tables)
            if missing:
                print(f"   ⚠️  Missing tables: {', '.join(missing)}")
            else:
                print("   ✅ All expected tables exist")
            
            return True
    except Exception as e:
        print(f"   ❌ Database tables check failed: {e}")
        return False


async def test_repositories():
    """Test basic repository operations."""
    print("\n🏛️  Testing repositories...")
    
    try:
        from src.database.connection import get_async_session
        from src.database.repositories import (
            LeadRepository,
            ProjectRepository,
            PropertyRepository,
            TypologyRepository,
        )
        
        async with get_async_session() as session:
            # Test Lead Repository
            lead_repo = LeadRepository(session)
            leads = await lead_repo.get_all(limit=1)
            print(f"   ✅ LeadRepository working (found {len(leads)} leads)")
            
            # Test Project Repository
            project_repo = ProjectRepository(session)
            projects = await project_repo.get_all(limit=1)
            print(f"   ✅ ProjectRepository working (found {len(projects)} projects)")
            
            # Test Property Repository
            property_repo = PropertyRepository(session)
            properties = await property_repo.get_all(limit=1)
            print(f"   ✅ PropertyRepository working (found {len(properties)} properties)")
            
            # Test Typology Repository
            typology_repo = TypologyRepository(session)
            typologies = await typology_repo.get_all(limit=1)
            print(f"   ✅ TypologyRepository working (found {len(typologies)} typologies)")
            
            return True
    except Exception as e:
        print(f"   ❌ Repository test failed: {e}")
        return False


async def test_cache_services():
    """Test cache services."""
    print("\n💾 Testing cache services...")
    
    try:
        from src.cache import get_redis_client, ConversationCache, SearchCache
        
        redis = get_redis_client()
        
        # Test ConversationCache
        conv_cache = ConversationCache(redis)
        test_conv_id = "test-conversation-123"
        
        await conv_cache.add_message(test_conv_id, "human", "Hola, busco un departamento")
        await conv_cache.add_message(test_conv_id, "assistant", "¡Hola! Con gusto te ayudo.")
        
        history = await conv_cache.get_history(test_conv_id)
        if len(history) == 2:
            print("   ✅ ConversationCache working")
        else:
            print(f"   ⚠️  ConversationCache issue: expected 2 messages, got {len(history)}")
        
        await conv_cache.clear(test_conv_id)
        
        # Test SearchCache
        search_cache = SearchCache(redis)
        test_query = "departamento 2 habitaciones miraflores"
        test_results = [{"id": "1", "title": "Test Property"}]
        
        await search_cache.set(test_query, test_results)
        cached = await search_cache.get(test_query)
        
        if cached and len(cached) == 1:
            print("   ✅ SearchCache working")
        else:
            print("   ⚠️  SearchCache issue")
        
        await search_cache.invalidate(test_query)
        
        return True
    except Exception as e:
        print(f"   ❌ Cache services test failed: {e}")
        return False


async def main():
    """Run all connection tests."""
    print("=" * 50)
    print("🧪 Pascal Real Estate - Connection Tests")
    print("=" * 50)
    
    results = []
    
    # Test PostgreSQL
    results.append(("PostgreSQL", await test_postgres_connection()))
    
    # Test Redis
    results.append(("Redis", await test_redis_connection()))
    
    # Test Database Tables
    results.append(("Database Tables", await test_database_tables()))
    
    # Test Repositories
    results.append(("Repositories", await test_repositories()))
    
    # Test Cache Services
    results.append(("Cache Services", await test_cache_services()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Connections are working.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

