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
    PROPERTY_INFO_SYSTEM_PROMPT,
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
    
    def _extract_property_id_from_message(self, message: str) -> Optional[UUID]:
        """
        Extract property UUID from message if present.
        
        Detects UUIDs in formats like:
        - "propiedad abc123-def456..."
        - "property id: abc123..."
        """
        # UUID pattern (standard format with dashes)
        uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        match = re.search(uuid_pattern, message)
        
        if match:
            try:
                return UUID(match.group())
            except ValueError:
                return None
        
        return None
    
    # Patterns for filter extraction (class-level for reuse)
    BEDROOM_PATTERNS = [
        ("1 dormitorio", 1), ("1 habitación", 1), ("1 cuarto", 1), ("1br", 1), ("un dormitorio", 1),
        ("2 dormitorios", 2), ("2 habitaciones", 2), ("2 cuartos", 2), ("2br", 2), ("dos dormitorios", 2),
        ("3 dormitorios", 3), ("3 habitaciones", 3), ("3 cuartos", 3), ("3br", 3), ("tres dormitorios", 3),
        ("4 dormitorios", 4), ("4 habitaciones", 4), ("4 cuartos", 4), ("4br", 4), ("cuatro dormitorios", 4),
        ("studio", 0), ("estudio", 0),
    ]
    
    DISTRICTS = {
        "miraflores": "Miraflores",
        "san isidro": "San Isidro",
        "surco": "Santiago de Surco",
        "santiago de surco": "Santiago de Surco",
        "barranco": "Barranco",
        "magdalena": "Magdalena del Mar",
        "jesus maria": "Jesús María",
        "jesús maría": "Jesús María",
        "lince": "Lince",
        "la molina": "La Molina",
        "surquillo": "Surquillo",
    }
    
    def _extract_filters_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract search filters from a single text string.
        Returns only the filters found in this specific text.
        """
        filters = {}
        text_lower = text.lower()
        
        # Number of bedrooms
        for pattern, num in self.BEDROOM_PATTERNS:
            if pattern in text_lower:
                filters["num_bedrooms"] = num
                break
        
        # District
        for key, value in self.DISTRICTS.items():
            if key in text_lower:
                filters["district"] = value
                break
        
        # Price range - improved patterns
        # Matches: $150,000 / $150.000 / 150000 / 150,000 / 150mil / 150k
        price_patterns = [
            # Standard format: $150,000 or 150.000
            (r'\$?\s*(\d{2,3})[,.](\d{3})', lambda m: int(m.group(1) + m.group(2))),
            # Short format: 150mil, 150k, 150M
            (r'(\d{2,3})\s*(?:mil|k|M)', lambda m: int(m.group(1)) * 1000),
            # Plain number (5-6 digits, likely a price)
            (r'\b(\d{5,6})\b', lambda m: int(m.group(1))),
        ]
        
        for pattern, extractor in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = extractor(match)
                # Determine if it's max or min price based on context
                if any(kw in text_lower for kw in ["menos de", "máximo", "hasta", "no más de", "tope"]):
                    filters["max_price"] = price
                elif any(kw in text_lower for kw in ["más de", "mínimo", "desde", "al menos"]):
                    filters["min_price"] = price
                else:
                    # Default: treat as max price (more common use case)
                    filters["max_price"] = price
                break
        
        # Property type
        if any(kw in text_lower for kw in ["departamento", "depa", "apartamento"]):
            filters["property_type"] = "departamento"
        elif any(kw in text_lower for kw in ["casa", "chalet"]):
            filters["property_type"] = "casa"
        elif any(kw in text_lower for kw in ["oficina"]):
            filters["property_type"] = "oficina"
        
        return filters
    
    def _extract_filters_from_message(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Extract search filters from conversation history and current message.
        
        Accumulates filters from oldest to newest messages, where newer values
        override older ones. Current message has highest priority.
        
        Args:
            message: Current user message
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
        
        Returns:
            Combined filters dictionary
        """
        accumulated_filters = {}
        
        # First, extract filters from conversation history (oldest to newest)
        if conversation_history:
            for msg in conversation_history:
                # Only extract from user messages
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    msg_filters = self._extract_filters_from_text(content)
                    # Update accumulated filters (newer overrides older)
                    accumulated_filters.update(msg_filters)
        
        # Finally, apply current message filters (highest priority)
        current_filters = self._extract_filters_from_text(message)
        accumulated_filters.update(current_filters)
        
        return accumulated_filters
    
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
        # First, check if the message contains a specific property ID
        property_id = self._extract_property_id_from_message(message)
        if property_id:
            # Direct lookup by ID
            property_data = await self.rag_service.get_property_by_id(property_id)
            if property_data:
                project_info = await self.rag_service.get_project_by_name(property_data["project_name"])
                # Generate response for this specific property
                response_text = await self._generate_response(
                    message=message,
                    properties=[property_data],
                    project_info=project_info,
                    conversation_history=conversation_history,
                )
                return {
                    "response": response_text,
                    "properties": [property_data],
                    "project": project_info,
                    "from": "PROPERTY_INFO"
                }
        
        # Extract filters from conversation history + current message
        filters = self._extract_filters_from_message(message, conversation_history)
        
        # If we have a recent project context, add it to filters
        """if recent_project_id:
            filters["project_id"] = recent_project_id"""
        
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
            "from": "PROPERTY_SEARCH"
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
            system_prompt = PROPERTY_INFO_SYSTEM_PROMPT.format(
                property_context=properties_context,
                recent_project=recent_project,
                conversation_history=history_context,
            )
        else:
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
