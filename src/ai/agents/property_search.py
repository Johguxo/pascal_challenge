"""
Property Search Agent - Handles property queries using RAG.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.providers import get_llm_provider
from src.ai.providers.base import Message
from src.ai.agents.prompts import (
    PROPERTY_SEARCH_SYSTEM_PROMPT,
    format_properties_context,
    format_conversation_history,
)
from src.ai.rag.search import RAGSearchService


class PropertySearchAgent:
    """
    Agent that handles property search queries using RAG.
    """
    
    def __init__(self, session: AsyncSession):
        self.llm = get_llm_provider()
        self.rag_service = RAGSearchService(session)
    
    def _extract_filters_from_message(self, message: str) -> Dict[str, Any]:
        """
        Extract search filters from natural language message.
        Simple keyword-based extraction.
        """
        filters = {}
        message_lower = message.lower()
        
        # Number of bedrooms
        bedroom_patterns = [
            ("1 dormitorio", 1), ("1 habitación", 1), ("1 cuarto", 1), ("1br", 1),
            ("2 dormitorios", 2), ("2 habitaciones", 2), ("2 cuartos", 2), ("2br", 2),
            ("3 dormitorios", 3), ("3 habitaciones", 3), ("3 cuartos", 3), ("3br", 3),
            ("4 dormitorios", 4), ("4 habitaciones", 4), ("4 cuartos", 4), ("4br", 4),
            ("studio", 0), ("estudio", 0),
        ]
        for pattern, num in bedroom_patterns:
            if pattern in message_lower:
                filters["num_bedrooms"] = num
                break
        
        # District
        districts = {
            "miraflores": "Miraflores",
            "san isidro": "San Isidro",
            "surco": "Santiago de Surco",
            "barranco": "Barranco",
            "magdalena": "Magdalena del Mar",
        }
        for key, value in districts.items():
            if key in message_lower:
                filters["district"] = value
                break
        
        # Price range (basic)
        price_match = re.search(r'\$?\s*(\d{2,3})[,.]?(\d{3})', message)
        if price_match:
            price = int(price_match.group(1) + price_match.group(2))
            if "menos" in message_lower or "máximo" in message_lower or "hasta" in message_lower:
                filters["max_price"] = price
            elif "más" in message_lower or "mínimo" in message_lower or "desde" in message_lower:
                filters["min_price"] = price
        
        return filters
    
    async def search(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        recent_project_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Search for properties based on user message.
        
        Returns:
            Dictionary with 'response' text and 'properties' list
        """
        # Extract filters
        filters = self._extract_filters_from_message(message)
        
        # If we have a recent project context, add it to filters
        if recent_project_id:
            filters["project_id"] = recent_project_id
        
        # Search properties using RAG
        properties = await self.rag_service.search_properties(
            query=message,
            filters=filters if filters else None,
            limit=5,
        )
        
        # Check if asking about a specific project
        project_info = None
        project_keywords = ["proyecto", "torre", "jardines", "loft", "residencial", "vista verde"]
        if any(kw in message.lower() for kw in project_keywords):
            # Extract project name and get details
            for keyword in ["torre pacífico", "jardines de surco", "loft san isidro", 
                          "residencial barranco", "vista verde"]:
                if keyword in message.lower():
                    project_info = await self.rag_service.get_project_by_name(keyword)
                    if project_info:
                        # Get properties for this project
                        project_properties = await self.rag_service.get_properties_for_project(
                            UUID(project_info["id"])
                        )
                        if project_properties:
                            properties = project_properties
                    break
        
        # Generate response using LLM
        response_text = await self._generate_response(
            message=message,
            properties=properties,
            project_info=project_info,
            conversation_history=conversation_history,
        )
        
        return {
            "response": response_text,
            "properties": properties,
            "project": project_info,
        }
    
    async def _generate_response(
        self,
        message: str,
        properties: List[Dict],
        project_info: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Generate natural language response."""
        
        # Build context
        properties_context = format_properties_context(properties)
        history_context = format_conversation_history(conversation_history or [])
        
        recent_project = "No hay proyecto reciente en la conversación."
        if project_info:
            recent_project = f"Proyecto: {project_info.get('name')} en {project_info.get('district')}"
        
        # Build prompt
        system_prompt = PROPERTY_SEARCH_SYSTEM_PROMPT.format(
            properties_context=properties_context,
            recent_project=recent_project,
            conversation_history=history_context,
        )
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=message),
        ]
        
        response = await self.llm.generate(messages, temperature=0.5)
        return response.content
