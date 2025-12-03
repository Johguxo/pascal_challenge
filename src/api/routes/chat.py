"""
Chat route - Main conversational endpoint.
This is a placeholder that will be fully implemented in Phase 4 (AI Module).
"""
from fastapi import APIRouter, Depends

from src.api.schemas.chat import ChatRequest, ChatResponse
from src.api.dependencies import get_db_session, get_conversation_cache
from src.database.repositories import LeadRepository, ConversationRepository
from src.cache import ConversationCache

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session=Depends(get_db_session),
    conv_cache: ConversationCache = Depends(get_conversation_cache),
):
    """
    Main chat endpoint.
    
    This endpoint will:
    1. Identify or create the user (lead)
    2. Get or create conversation
    3. Classify intent using Orchestrator Agent
    4. Route to appropriate agent (Onboarding, PropertySearch, Schedule)
    5. Return structured response
    
    Currently returns a placeholder response.
    Full implementation in Phase 4 (AI Module).
    """
    lead_repo = LeadRepository(session)
    conv_repo = ConversationRepository(session)
    
    # Get or create lead
    if request.channel_user_id:
        lead, _ = await lead_repo.get_or_create_by_telegram_chat_id(
            request.channel_user_id,
            name=request.user_name,
        )
    else:
        # Web session - create anonymous lead or use session_id
        lead = await lead_repo.create(
            telegram_chat_id=None,
            name=request.user_name or "Web User",
        )
    
    # Get or create conversation
    conversation, _ = await conv_repo.get_or_create_for_lead(lead.id)
    
    # Cache the user message
    await conv_cache.add_message(
        str(conversation.id),
        role="human",
        content=request.message,
    )
    
    # TODO: Implement in Phase 4
    # 1. Get conversation history from cache
    # 2. Classify intent with Orchestrator
    # 3. Route to appropriate agent
    # 4. Generate response
    # 5. Cache assistant response
    
    # Placeholder response
    response_text = (
        f"¡Hola! Recibí tu mensaje: '{request.message}'. "
        "El sistema de agentes se implementará en la Fase 4. "
        "Por ahora, la API está funcionando correctamente."
    )
    
    # Cache the assistant response
    await conv_cache.add_message(
        str(conversation.id),
        role="assistant",
        content=response_text,
    )
    
    return ChatResponse(
        type="ONBOARDING",
        response=response_text,
        conversation_id=conversation.id,
        debug={
            "intent": "PLACEHOLDER",
            "cached": False,
        }
    )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    conv_cache: ConversationCache = Depends(get_conversation_cache),
):
    """Get chat history for a session (from cache)."""
    history = await conv_cache.get_history_for_llm(session_id)
    return {"messages": history}

