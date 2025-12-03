"""
Message routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.messages import MessageCreate, MessageResponse
from src.api.dependencies import get_db_session
from src.database.repositories import MessageRepository
from src.database.models import MessageType

router = APIRouter()


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: UUID,
    session=Depends(get_db_session),
):
    """Get a message by ID."""
    repo = MessageRepository(session)
    message = await repo.get_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_message(
    data: MessageCreate,
    session=Depends(get_db_session),
):
    """Create a new message."""
    repo = MessageRepository(session)
    
    # Convert string enum to model enum
    msg_type = MessageType.human if data.type == "human" else MessageType.ai_assistant
    
    message = await repo.create(
        conversation_id=data.conversation_id,
        content=data.content,
        message_type=msg_type,
    )
    return message

