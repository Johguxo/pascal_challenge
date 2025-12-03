"""
Onboarding Agent - Handles greetings and general questions.
"""
from typing import Optional, List, Dict

from src.ai.providers import get_llm_provider
from src.ai.providers.base import Message
from src.ai.agents.prompts import ONBOARDING_SYSTEM_PROMPT


class OnboardingAgent:
    """
    Agent that handles onboarding, greetings, and general questions.
    """
    
    def __init__(self):
        self.llm = get_llm_provider()
    
    async def respond(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_name: Optional[str] = None,
    ) -> str:
        """
        Generate a friendly onboarding response.
        
        Args:
            message: User's message
            conversation_history: Previous messages
            user_name: User's name if known
        
        Returns:
            Response text
        """
        # Build messages
        messages = [Message(role="system", content=ONBOARDING_SYSTEM_PROMPT)]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-3:]:  # Last 3 messages
                if msg.get("role") == "user":
                    messages.append(Message(role="user", content=msg["content"]))
                else:
                    messages.append(Message(role="assistant", content=msg["content"]))
        
        # Add current message
        if user_name:
            messages.append(Message(role="user", content=f"[Usuario: {user_name}] {message}"))
        else:
            messages.append(Message(role="user", content=message))
        
        response = await self.llm.generate(messages, temperature=0.7)
        return response.content
    
    def get_welcome_message(self, user_name: Optional[str] = None) -> str:
        """Get a welcome message for new users."""
        name_part = f" {user_name}" if user_name else ""
        return (
            f"¡Hola{name_part}! 👋 Soy Pascal, tu asistente inmobiliario.\n\n"
            "Puedo ayudarte a:\n"
            "🏠 Buscar departamentos en Lima\n"
            "📋 Darte información sobre proyectos\n"
            "📅 Agendar visitas\n\n"
            "¿En qué puedo ayudarte hoy?"
        )
