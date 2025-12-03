"""
Chat route - Main conversational endpoint.
"""
from fastapi import APIRouter, Depends

from src.api.schemas.chat import ChatRequest, ChatResponse, PropertyItem, AppointmentInfo, ChatDebugInfo
from src.api.dependencies import get_db_session, get_conversation_cache
from src.ai.chat_service import ChatService
from src.cache import ConversationCache

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session=Depends(get_db_session),
):
    """
    Main chat endpoint.
    
    This endpoint:
    1. Identifies or creates the user (lead)
    2. Gets or creates conversation
    3. Classifies intent using Orchestrator Agent
    4. Routes to appropriate agent (Onboarding, PropertySearch, Schedule)
    5. Returns structured response
    """
    # Initialize chat service
    chat_service = ChatService(session)
    
    # Process the message
    result = await chat_service.process_message(
        message=request.message,
        channel=request.channel,
        channel_user_id=request.channel_user_id,
        user_name=request.user_name,
        session_id=request.session_id,
    )
    
    # Build response
    properties = None
    if result.get("properties"):
        properties = [
            PropertyItem(
                id=p["id"],
                title=p.get("title"),
                project_name=p.get("project_name"),
                price_usd=p.get("price_usd"),
                bedrooms=p.get("bedrooms"),
                bathrooms=p.get("bathrooms"),
                district=p.get("district"),
                floor=p.get("floor"),
                area_m2=p.get("area_m2"),
            )
            for p in result["properties"]
        ]
    
    appointment = None
    if result.get("appointment"):
        apt = result["appointment"]
        appointment = AppointmentInfo(
            id=apt["id"],
            scheduled_for=apt.get("scheduled_for"),
            project_name=apt.get("project_name"),
            property_title=apt.get("property_title"),
        )
    
    debug = None
    if result.get("debug"):
        debug = ChatDebugInfo(
            intent=result["debug"].get("intent"),
            rag_results_count=result["debug"].get("rag_results_count"),
            cached=result["debug"].get("cached", False),
            processing_time_ms=result["debug"].get("processing_time_ms"),
        )
    
    return ChatResponse(
        type=result["type"],
        response=result["response"],
        summary=result.get("summary"),
        properties=properties,
        appointment=appointment,
        suggested_actions=result.get("suggested_actions"),
        conversation_id=result.get("conversation_id"),
        debug=debug,
    )


@router.get("/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    conv_cache: ConversationCache = Depends(get_conversation_cache),
):
    """Get chat history for a conversation (from cache)."""
    history = await conv_cache.get_history_for_llm(conversation_id)
    return {"messages": history}
