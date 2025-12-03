"""
FastAPI dependencies for dependency injection.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import AsyncSessionLocal
from src.database.repositories import (
    LeadRepository,
    ConversationRepository,
    MessageRepository,
    ProjectRepository,
    PropertyRepository,
    TypologyRepository,
    AppointmentRepository,
)
from src.cache import get_redis_client, ConversationCache, SearchCache


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Repository dependencies
async def get_lead_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[LeadRepository, None]:
    """Get Lead repository."""
    async for session in get_db_session():
        yield LeadRepository(session)


async def get_conversation_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[ConversationRepository, None]:
    """Get Conversation repository."""
    async for session in get_db_session():
        yield ConversationRepository(session)


async def get_message_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[MessageRepository, None]:
    """Get Message repository."""
    async for session in get_db_session():
        yield MessageRepository(session)


async def get_project_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[ProjectRepository, None]:
    """Get Project repository."""
    async for session in get_db_session():
        yield ProjectRepository(session)


async def get_property_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[PropertyRepository, None]:
    """Get Property repository."""
    async for session in get_db_session():
        yield PropertyRepository(session)


async def get_typology_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[TypologyRepository, None]:
    """Get Typology repository."""
    async for session in get_db_session():
        yield TypologyRepository(session)


async def get_appointment_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[AppointmentRepository, None]:
    """Get Appointment repository."""
    async for session in get_db_session():
        yield AppointmentRepository(session)


# Cache dependencies
def get_conversation_cache() -> ConversationCache:
    """Get conversation cache service."""
    return ConversationCache(get_redis_client())


def get_search_cache() -> SearchCache:
    """Get search cache service."""
    return SearchCache(get_redis_client())

