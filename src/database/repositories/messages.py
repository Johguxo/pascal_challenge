"""
Message repository for database operations.
"""
import uuid
from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Message, MessageType
from src.database.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)
    
    async def create(
        self,
        conversation_id: uuid.UUID,
        content: str,
        message_type: MessageType,
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            type=message_type,
        )
        self.session.add(message)
        await self.session.flush()
        return message
    
    async def get_by_conversation(
        self,
        conversation_id: uuid.UUID,
        limit: int = 100,
    ) -> List[Message]:
        """Get all messages for a conversation in chronological order."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent(
        self,
        conversation_id: uuid.UUID,
        limit: int = 5,
    ) -> List[Message]:
        """Get recent messages for a conversation (for context)."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return in chronological order

