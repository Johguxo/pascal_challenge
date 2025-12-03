"""
Main Chat Service - Orchestrates agents and manages conversation flow.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
import time

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.agents import (
    OrchestratorAgent,
    Intent,
    OnboardingAgent,
    PropertySearchAgent,
    ScheduleAgent,
)
from src.cache import ConversationCache, get_redis_client
from src.database.repositories import (
    LeadRepository,
    ConversationRepository,
)
from src.database.models import MessageType


class ChatService:
    """
    Main service that handles chat flow.
    
    Flow:
    1. Identify/create user (lead)
    2. Get/create conversation
    3. Classify intent with Orchestrator
    4. Route to appropriate agent
    5. Store messages and return response
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadRepository(session)
        self.conv_repo = ConversationRepository(session)
        self.conv_cache = ConversationCache(get_redis_client())
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent()
        self.onboarding_agent = OnboardingAgent()
        self.property_agent = PropertySearchAgent(session)
        self.schedule_agent = ScheduleAgent(session)
    
    async def process_message(
        self,
        message: str,
        channel: str = "web",
        channel_user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming chat message.
        
        Args:
            message: User's message text
            channel: Channel (web, telegram, whatsapp)
            channel_user_id: User ID from the channel
            user_name: User's name if known
            session_id: Session ID for web users
        
        Returns:
            Structured response dict
        """
        start_time = time.time()
        
        # 1. Get or create lead
        lead, lead_created = await self._get_or_create_lead(
            channel=channel,
            channel_user_id=channel_user_id,
            user_name=user_name,
        )
        
        # 2. Get or create conversation
        conversation, conv_created = await self.conv_repo.get_or_create_for_lead(lead.id)
        
        # 3. Get conversation history from cache
        history = await self.conv_cache.get_history_for_llm(str(conversation.id))
        
        # 4. Classify intent
        intent = await self.orchestrator.route(message, history)
        
        # 5. Route to appropriate agent
        if intent == Intent.ONBOARDING_SMALL_TALK:
            result = await self._handle_onboarding(
                message=message,
                history=history,
                user_name=user_name or lead.name,
                is_new_user=lead_created or conv_created,
            )
        elif intent == Intent.PROPERTY_SEARCH:
            result = await self._handle_property_search(
                message=message,
                history=history,
                conversation=conversation,
            )
        elif intent == Intent.SCHEDULE_VISIT:
            result = await self._handle_schedule(
                message=message,
                history=history,
                lead_id=lead.id,
                conversation=conversation,
            )
        else:
            result = await self._handle_onboarding(message, history, user_name)
        
        # 6. Store messages
        await self._store_messages(
            conversation_id=conversation.id,
            user_message=message,
            assistant_message=result["response"],
        )
        
        # 7. Update conversation cache
        await self.conv_cache.add_message(
            str(conversation.id),
            role="human",
            content=message,
        )
        await self.conv_cache.add_message(
            str(conversation.id),
            role="assistant",
            content=result["response"],
        )
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response
        return {
            "type": result.get("type", "ONBOARDING"),
            "response": result["response"],
            "summary": result.get("summary"),
            "properties": result.get("properties"),
            "appointment": result.get("appointment"),
            "suggested_actions": result.get("suggested_actions"),
            "conversation_id": conversation.id,
            "debug": {
                "intent": intent.value,
                "rag_results_count": len(result.get("properties", [])) if result.get("properties") else None,
                "cached": False,
                "processing_time_ms": processing_time,
            },
        }
    
    async def _get_or_create_lead(
        self,
        channel: str,
        channel_user_id: Optional[str],
        user_name: Optional[str],
    ):
        """Get existing lead or create new one."""
        if channel == "telegram" and channel_user_id:
            return await self.lead_repo.get_or_create_by_telegram_chat_id(
                channel_user_id,
                name=user_name,
            )
        else:
            # Web or other - create new lead
            lead = await self.lead_repo.create(
                telegram_chat_id=None,
                name=user_name or "Web User",
            )
            return lead, True
    
    async def _handle_onboarding(
        self,
        message: str,
        history: List[Dict],
        user_name: Optional[str] = None,
        is_new_user: bool = False,
    ) -> Dict[str, Any]:
        """Handle onboarding/small talk."""
        if is_new_user and not history:
            # First message - send welcome
            response = self.onboarding_agent.get_welcome_message(user_name)
        else:
            response = await self.onboarding_agent.respond(
                message=message,
                conversation_history=history,
                user_name=user_name,
            )
        
        return {
            "type": "ONBOARDING",
            "response": response,
            "suggested_actions": ["buscar_propiedad", "ver_proyectos"],
        }
    
    async def _handle_property_search(
        self,
        message: str,
        history: List[Dict],
        conversation,
    ) -> Dict[str, Any]:
        """Handle property search."""
        result = await self.property_agent.search(
            message=message,
            conversation_history=history,
            recent_project_id=conversation.most_recent_project_id,
        )
        
        # Update most recent project if found
        if result.get("project") and result["project"].get("id"):
            await self.conv_repo.update_most_recent_project(
                conversation.id,
                UUID(result["project"]["id"]),
            )
        
        properties = result.get("properties", [])
        
        return {
            "type": "PROPERTY_SEARCH_RESULT",
            "response": result["response"],
            "summary": f"Encontré {len(properties)} propiedades" if properties else None,
            "properties": [
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "project_name": p.get("project_name"),
                    "price_usd": p.get("price_usd"),
                    "bedrooms": p.get("bedrooms"),
                    "bathrooms": p.get("bathrooms"),
                    "district": p.get("district"),
                    "floor": p.get("floor"),
                    "area_m2": p.get("area_m2"),
                }
                for p in properties
            ],
            "suggested_actions": ["agendar_visita", "ver_mas_opciones"],
        }
    
    async def _handle_schedule(
        self,
        message: str,
        history: List[Dict],
        lead_id: UUID,
        conversation,
    ) -> Dict[str, Any]:
        """Handle appointment scheduling."""
        result = await self.schedule_agent.process(
            message=message,
            lead_id=lead_id,
            conversation_id=conversation.id,
            conversation_history=history,
            recent_project_id=conversation.most_recent_project_id,
        )
        
        response_type = "SCHEDULE_CONFIRMATION" if result.get("scheduled") else "SCHEDULE_REQUEST"
        
        return {
            "type": response_type,
            "response": result["response"],
            "appointment": result.get("appointment"),
            "suggested_actions": ["buscar_otra_propiedad"] if result.get("scheduled") else ["confirmar_cita"],
        }
    
    async def _store_messages(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
    ):
        """Store messages in database."""
        # Store user message
        await self.conv_repo.add_message(
            conversation_id=conversation_id,
            content=user_message,
            message_type=MessageType.human,
        )
        
        # Store assistant message
        await self.conv_repo.add_message(
            conversation_id=conversation_id,
            content=assistant_message,
            message_type=MessageType.ai_assistant,
        )

