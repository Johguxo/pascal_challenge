"""
Schedule Agent - Handles appointment scheduling.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.providers import get_llm_provider
from src.ai.providers.base import Message
from src.ai.agents.prompts import (
    SCHEDULE_SYSTEM_PROMPT,
    format_conversation_history,
)
from src.database.repositories import AppointmentRepository, ProjectRepository


class ScheduleAgent:
    """
    Agent that handles appointment scheduling for property visits.
    """
    
    def __init__(self, session: AsyncSession):
        self.llm = get_llm_provider()
        self.session = session
        self.appointment_repo = AppointmentRepository(session)
        self.project_repo = ProjectRepository(session)
    
    def _extract_datetime(self, message: str) -> Optional[datetime]:
        """
        Extract date/time from message.
        Simple pattern matching for common expressions.
        """
        message_lower = message.lower()
        now = datetime.now()
        
        # Day patterns
        if "mañana" in message_lower and "por la" not in message_lower:
            target_date = now + timedelta(days=1)
        elif "pasado mañana" in message_lower:
            target_date = now + timedelta(days=2)
        elif "lunes" in message_lower:
            days_ahead = (0 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "martes" in message_lower:
            days_ahead = (1 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "miércoles" in message_lower or "miercoles" in message_lower:
            days_ahead = (2 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "jueves" in message_lower:
            days_ahead = (3 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "viernes" in message_lower:
            days_ahead = (4 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "sábado" in message_lower or "sabado" in message_lower:
            days_ahead = (5 - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_ahead)
        elif "domingo" in message_lower:
            # No appointments on Sunday
            return None
        else:
            target_date = now + timedelta(days=1)  # Default to tomorrow
        
        # Time patterns
        hour = 10  # Default to 10am
        
        if "mañana" in message_lower and "por la" in message_lower:
            hour = 10
        elif "tarde" in message_lower:
            hour = 15
        elif "noche" in message_lower:
            hour = 18
        
        # Specific hour
        time_match = re.search(r'(\d{1,2})\s*(?::|h|hrs?|am|pm)?', message_lower)
        if time_match:
            parsed_hour = int(time_match.group(1))
            if "pm" in message_lower and parsed_hour < 12:
                parsed_hour += 12
            if 9 <= parsed_hour <= 18:
                hour = parsed_hour
        
        return target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    async def process(
        self,
        message: str,
        lead_id: UUID,
        conversation_id: UUID,
        conversation_history: Optional[List[Dict]] = None,
        recent_project_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Process scheduling request.
        
        Returns:
            Dictionary with 'response' text and optional 'appointment' data
        """
        # Try to extract datetime
        scheduled_for = self._extract_datetime(message)
        
        # Get project context
        project_info = None
        if recent_project_id:
            project = await self.project_repo.get_by_id(recent_project_id)
            if project:
                project_info = {
                    "id": str(project.id),
                    "name": project.name,
                    "district": project.district,
                    "address": project.address,
                }
        
        # Check if we have enough info to schedule
        can_schedule = scheduled_for is not None and project_info is not None
        
        if can_schedule:
            # Check availability
            is_available = await self.appointment_repo.check_availability(
                scheduled_for,
                recent_project_id,
            )
            
            if is_available:
                # Create appointment
                appointment = await self.appointment_repo.create(
                    lead_id=lead_id,
                    conversation_id=conversation_id,
                    project_id=recent_project_id,
                    scheduled_for=scheduled_for,
                    notes=f"Agendado via chat: {message}",
                )
                
                response_text = self._format_confirmation(
                    scheduled_for=scheduled_for,
                    project_info=project_info,
                )
                
                return {
                    "response": response_text,
                    "appointment": {
                        "id": str(appointment.id),
                        "scheduled_for": scheduled_for.isoformat(),
                        "project_name": project_info["name"],
                        "project_address": project_info.get("address"),
                    },
                    "scheduled": True,
                }
            else:
                response_text = (
                    "Lo siento, ese horario no está disponible. "
                    "¿Te gustaría agendar en otro momento? "
                    "Tenemos disponibilidad de lunes a sábado, de 9am a 6pm."
                )
                return {
                    "response": response_text,
                    "appointment": None,
                    "scheduled": False,
                }
        
        # Need more info - generate response asking for details
        response_text = await self._generate_response(
            message=message,
            project_info=project_info,
            conversation_history=conversation_history,
            scheduled_for=scheduled_for,
        )
        
        return {
            "response": response_text,
            "appointment": None,
            "scheduled": False,
        }
    
    def _format_confirmation(
        self,
        scheduled_for: datetime,
        project_info: Dict,
    ) -> str:
        """Format appointment confirmation message."""
        day_names = {
            0: "Lunes", 1: "Martes", 2: "Miércoles",
            3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
        }
        
        day_name = day_names[scheduled_for.weekday()]
        date_str = scheduled_for.strftime(f"{day_name} %d/%m/%Y")
        time_str = scheduled_for.strftime("%H:%M")
        
        return (
            f"✅ ¡Excelente! Tu visita ha sido agendada.\n\n"
            f"📅 Fecha: {date_str}\n"
            f"🕐 Hora: {time_str}\n"
            f"🏢 Proyecto: {project_info['name']}\n"
            f"📍 Ubicación: {project_info.get('district', 'Lima')}\n"
            f"🗺️ Dirección: {project_info.get('address', 'Por confirmar')}\n\n"
            "Te contactaremos para confirmar los detalles. "
            "¿Hay algo más en lo que pueda ayudarte?"
        )
    
    async def _generate_response(
        self,
        message: str,
        project_info: Optional[Dict],
        conversation_history: Optional[List[Dict]],
        scheduled_for: Optional[datetime],
    ) -> str:
        """Generate response asking for missing info."""
        
        # Build context
        lead_info = "Usuario registrado en el sistema."
        property_context = "Sin proyecto seleccionado."
        if project_info:
            property_context = f"Proyecto: {project_info['name']} en {project_info.get('district', 'Lima')}"
        
        history_context = format_conversation_history(conversation_history or [])
        
        system_prompt = SCHEDULE_SYSTEM_PROMPT.format(
            lead_info=lead_info,
            property_context=property_context,
            conversation_history=history_context,
        )
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=message),
        ]
        
        response = await self.llm.generate(messages, temperature=0.3)
        return response.content
