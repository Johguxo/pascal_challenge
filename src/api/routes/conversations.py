"""
Conversation routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.conversations import ConversationCreate, ConversationResponse
from src.api.schemas.messages import MessageResponse
from src.api.dependencies import get_db_session
from src.database.repositories import ConversationRepository

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all conversations."""
    repo = ConversationRepository(session)
    conversations = await repo.get_all(skip=skip, limit=limit)
    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    session=Depends(get_db_session),
):
    """Get a conversation by ID."""
    repo = ConversationRepository(session)
    conversation = await repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 50,
    session=Depends(get_db_session),
):
    """Get messages for a conversation."""
    repo = ConversationRepository(session)
    conversation = await repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await repo.get_recent_messages(conversation_id, limit=limit)
    return messages


@router.get("/lead/{lead_id}", response_model=List[ConversationResponse])
async def get_conversations_by_lead(
    lead_id: UUID,
    session=Depends(get_db_session),
):
    """Get all conversations for a lead."""
    repo = ConversationRepository(session)
    # Get active conversation (most recent)
    conversation = await repo.get_active_for_lead(lead_id)
    if conversation:
        return [conversation]
    return []


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    session=Depends(get_db_session),
):
    """Create a new conversation."""
    repo = ConversationRepository(session)
    conversation = await repo.create(lead_id=data.lead_id)
    return conversation

