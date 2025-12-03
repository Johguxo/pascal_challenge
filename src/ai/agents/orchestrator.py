"""
Orchestrator Agent - Classifies user intent and routes to appropriate agent.
"""
from enum import Enum
from typing import Optional

from src.ai.providers import get_llm_provider
from src.ai.providers.base import Message
from src.ai.agents.prompts import ORCHESTRATOR_SYSTEM_PROMPT


class Intent(str, Enum):
    """User intent categories."""
    ONBOARDING_SMALL_TALK = "ONBOARDING_SMALL_TALK"
    PROPERTY_SEARCH = "PROPERTY_SEARCH"
    SCHEDULE_VISIT = "SCHEDULE_VISIT"


class OrchestratorAgent:
    """
    Agent that classifies user messages into intents.
    Routes to the appropriate specialized agent.
    """
    
    def __init__(self):
        self.llm = get_llm_provider()
    
    async def classify(
        self,
        message: str,
        conversation_history: Optional[list] = None,
    ) -> Intent:
        """
        Classify the user message into an intent.
        
        Args:
            message: The user's message
            conversation_history: Optional previous messages for context
        
        Returns:
            Intent enum value
        """
        messages = [
            Message(role="system", content=ORCHESTRATOR_SYSTEM_PROMPT),
            Message(role="user", content=message),
        ]
        
        response = await self.llm.generate(messages, temperature=0)
        result = response.content.strip().upper()
        
        # Parse result
        try:
            # Handle variations
            if "PROPERTY" in result or "SEARCH" in result:
                return Intent.PROPERTY_SEARCH
            elif "SCHEDULE" in result or "VISIT" in result:
                return Intent.SCHEDULE_VISIT
            elif "ONBOARDING" in result or "SMALL_TALK" in result:
                return Intent.ONBOARDING_SMALL_TALK
            else:
                # Default to onboarding for unknown
                return Intent.ONBOARDING_SMALL_TALK
        except Exception:
            return Intent.ONBOARDING_SMALL_TALK
    
    def classify_with_heuristics(self, message: str) -> Optional[Intent]:
        """
        Fast heuristic classification for common patterns.
        Returns None if LLM should be used.
        """
        message_lower = message.lower().strip()
        
        # Pure greetings
        greetings = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches", "hi", "hello"]
        if message_lower in greetings:
            return Intent.ONBOARDING_SMALL_TALK
        
        # Schedule keywords
        schedule_keywords = ["agendar", "visita", "cita", "visitarlos", "ir a ver", "conocer el proyecto"]
        if any(kw in message_lower for kw in schedule_keywords):
            return Intent.SCHEDULE_VISIT
        
        # Property search keywords
        search_keywords = [
            "busco", "departamento", "depa", "habitación", "habitaciones", 
            "dormitorio", "precio", "cuánto", "miraflores", "san isidro",
            "surco", "barranco", "proyecto", "disponible", "piso"
        ]
        if any(kw in message_lower for kw in search_keywords):
            return Intent.PROPERTY_SEARCH
        
        # Use LLM for ambiguous cases
        return None
    
    async def route(
        self,
        message: str,
        conversation_history: Optional[list] = None,
    ) -> Intent:
        """
        Route message to appropriate intent, using heuristics first.
        """
        # Try heuristics first (faster)
        intent = self.classify_with_heuristics(message)
        if intent:
            return intent
        
        # Fall back to LLM for complex cases
        return await self.classify(message, conversation_history)
