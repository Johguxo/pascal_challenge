"""
Conversation repository for database operations.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Conversation, Message, MessageType
from src.database.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
    
    async def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Get conversation by ID with messages."""
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_for_lead(self, lead_id: uuid.UUID) -> Optional[Conversation]:
        """Get the most recent conversation for a lead."""
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.lead_id == lead_id)
            .order_by(desc(Conversation.updated_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create(self, lead_id: uuid.UUID) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            lead_id=lead_id,
            last_message_at=datetime.utcnow(),
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation
    
    async def get_or_create_for_lead(self, lead_id: uuid.UUID) -> tuple[Conversation, bool]:
        """Get existing active conversation or create new one."""
        existing = await self.get_active_for_lead(lead_id)
        if existing:
            return existing, False
        
        new_conv = await self.create(lead_id)
        return new_conv, True
    
    async def add_message(
        self, 
        conversation_id: uuid.UUID, 
        content: str, 
        message_type: MessageType
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            type=message_type,
        )
        self.session.add(message)
        
        # Update conversation timestamp
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()
        conversation.last_message_at = datetime.utcnow()
        
        await self.session.flush()
        return message
    
    async def get_recent_messages(
        self, 
        conversation_id: uuid.UUID, 
        limit: int = 5
    ) -> List[Message]:
        """Get recent messages for a conversation."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
    
    async def update_most_recent_project(
        self, 
        conversation_id: uuid.UUID, 
        project_id: uuid.UUID
    ) -> None:
        """Update the most recent project for a conversation."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()
        conversation.most_recent_project_id = project_id
        await self.session.flush()

