"""
Telegram message handlers.
Processes incoming messages and routes to appropriate handlers.
"""
from typing import Dict, Any, Optional
import logging

from src.bff.telegram.bot import TelegramBot, TelegramMessage, CallbackQuery
from src.bff.telegram.formatters import TelegramFormatter
from src.bff.telegram.keyboards import (
    create_property_keyboard,
    create_schedule_keyboard,
    create_main_menu_keyboard,
    create_suggested_actions_keyboard,
    create_schedule_time_keyboard,
)
from src.ai.chat_service import ChatService
from src.database.connection import get_async_session

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles incoming Telegram messages and callbacks.
    Routes to appropriate response handlers.
    """
    
    def __init__(self, bot: TelegramBot):
        self.bot = bot
        self.formatter = TelegramFormatter()
    
    async def handle_update(self, update: Dict[str, Any]) -> None:
        """
        Handle an incoming Telegram update.
        
        Args:
            update: Raw update from Telegram webhook
        """
        try:
            if "message" in update:
                message = TelegramMessage.from_dict(update["message"])
                await self.handle_message(message)
            
            elif "callback_query" in update:
                callback = CallbackQuery.from_dict(update["callback_query"])
                await self.handle_callback(callback)
            
            else:
                logger.debug(f"Unhandled update type: {update.keys()}")
        
        except Exception as e:
            logger.error(f"Error handling update: {e}", exc_info=True)
            # Try to send error message if we have chat_id
            chat_id = self._extract_chat_id(update)
            if chat_id:
                await self._send_error(chat_id)
    
    def _extract_chat_id(self, update: Dict[str, Any]) -> Optional[int]:
        """Extract chat_id from any update type."""
        if "message" in update:
            return update["message"].get("chat", {}).get("id")
        elif "callback_query" in update:
            return update["callback_query"].get("message", {}).get("chat", {}).get("id")
        return None
    
    async def handle_message(self, message: TelegramMessage) -> None:
        """
        Handle a text message.
        
        Args:
            message: Parsed Telegram message
        """
        chat_id = message.chat_id
        text = message.text
        user = message.user
        
        if not text:
            return
        
        # Handle commands
        if text.startswith("/"):
            await self.handle_command(message)
            return
        
        # Show typing indicator
        await self.bot.send_chat_action(chat_id, "typing")
        
        # Process through chat service
        async with get_async_session() as session:
            chat_service = ChatService(session)
            
            result = await chat_service.process_message(
                message=text,
                channel="telegram",
                channel_user_id=str(user.id),
                user_name=user.full_name,
            )
        
        # Format and send response
        await self._send_chat_response(chat_id, result)
    
    async def handle_command(self, message: TelegramMessage) -> None:
        """
        Handle bot commands.
        
        Args:
            message: Message containing command
        """
        chat_id = message.chat_id
        command = message.text.split()[0].lower()
        user = message.user
        
        if command == "/start":
            welcome = self.formatter.format_welcome(user.first_name)
            await self.bot.send_message(
                chat_id=chat_id,
                text=welcome,
                reply_markup=create_main_menu_keyboard(),
            )
        
        elif command == "/menu":
            await self.bot.send_message(
                chat_id=chat_id,
                text="¿En qué puedo ayudarte?",
                reply_markup=create_main_menu_keyboard(),
            )
        
        elif command == "/buscar":
            await self.bot.send_message(
                chat_id=chat_id,
                text="🔍 ¿Qué tipo de propiedad buscas?\n\n"
                     "Puedes decirme algo como:\n"
                     "• _Busco un departamento de 2 habitaciones_\n"
                     "• _Necesito algo en Miraflores_\n"
                     "• _Departamento con vista al mar_",
            )
        
        elif command == "/proyectos":
            # Send message prompting for project search
            async with get_async_session() as session:
                chat_service = ChatService(session)
                result = await chat_service.process_message(
                    message="¿Qué proyectos tienen disponibles?",
                    channel="telegram",
                    channel_user_id=str(user.id),
                )
            await self._send_chat_response(chat_id, result)
        
        elif command == "/agendar":
            await self.bot.send_message(
                chat_id=chat_id,
                text="📅 Para agendar una visita, primero dime:\n"
                     "¿Qué proyecto o propiedad te gustaría visitar?",
            )
        
        elif command == "/ayuda" or command == "/help":
            help_text = """📚 *Comandos disponibles:*

/start - Iniciar conversación
/menu - Ver menú principal
/buscar - Buscar propiedades
/proyectos - Ver proyectos disponibles
/agendar - Agendar una visita
/ayuda - Ver esta ayuda

También puedes escribirme directamente lo que necesitas. Por ejemplo:
• _Busco un depa de 2 habitaciones en Miraflores_
• _¿Cuánto cuesta el proyecto Torre Pacífico?_
• _Quiero agendar una visita para el sábado_"""
            
            await self.bot.send_message(chat_id=chat_id, text=help_text)
        
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text="Comando no reconocido. Usa /ayuda para ver los comandos disponibles.",
            )
    
    async def handle_callback(self, callback: CallbackQuery) -> None:
        """
        Handle callback query from inline keyboard.
        
        Args:
            callback: Parsed callback query
        """
        chat_id = callback.chat_id
        data = callback.data
        user = callback.user
        
        # Acknowledge the callback
        await self.bot.answer_callback_query(callback.id)
        
        # Parse callback data
        if ":" in data:
            action, value = data.split(":", 1)
        else:
            action, value = data, ""
        # Route to appropriate handler
        if action == "property":
            await self._handle_property_callback(chat_id, value, user)
        
        elif action == "project":
            await self._handle_project_callback(chat_id, value, user)
        
        elif action == "schedule":
            await self._handle_schedule_callback(chat_id, value, user)
        
        elif action == "time":
            await self._handle_time_callback(chat_id, value, user)
        
        elif action == "menu":
            await self._handle_menu_callback(chat_id, value, user)
        
        elif action == "action":
            await self._handle_action_callback(chat_id, value, user)
        
        elif action == "confirm":
            await self._handle_confirm_callback(chat_id, value, user)
    
    async def _handle_property_callback(
        self,
        chat_id: int,
        property_id: str,
        user: Any,
    ) -> None:
        """Handle property selection callback."""
        await self.bot.send_chat_action(chat_id, "typing")
        
        async with get_async_session() as session:
            chat_service = ChatService(session)
            result = await chat_service.process_message(
                message=f"Dame más información sobre la propiedad {property_id}",
                channel="telegram",
                channel_user_id=str(user.id),
            )
        
        await self._send_chat_response(chat_id, result)
    
    async def _handle_project_callback(
        self,
        chat_id: int,
        project_id: str,
        user: Any,
    ) -> None:
        """Handle project selection callback."""
        await self.bot.send_chat_action(chat_id, "typing")
        
        async with get_async_session() as session:
            chat_service = ChatService(session)
            result = await chat_service.process_message(
                message=f"Información del proyecto {project_id}",
                channel="telegram",
                channel_user_id=str(user.id),
            )
        
        await self._send_chat_response(chat_id, result)
    
    async def _handle_schedule_callback(
        self,
        chat_id: int,
        value: str,
        user: Any,
    ) -> None:
        """Handle scheduling callback."""
        day_text = "mañana" if value == "tomorrow" else "pasado mañana"
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=f"📅 Seleccionaste *{day_text}*. ¿A qué hora te gustaría la visita?",
            reply_markup=create_schedule_time_keyboard(),
        )
    
    async def _handle_time_callback(
        self,
        chat_id: int,
        value: str,
        user: Any,
    ) -> None:
        """Handle time selection callback."""
        time_text = "10:00 AM" if value == "morning" else "3:00 PM"
        
        async with get_async_session() as session:
            chat_service = ChatService(session)
            result = await chat_service.process_message(
                message=f"Quiero agendar una visita a las {time_text}",
                channel="telegram",
                channel_user_id=str(user.id),
            )
        
        await self._send_chat_response(chat_id, result)
    
    async def _handle_menu_callback(
        self,
        chat_id: int,
        value: str,
        user: Any,
    ) -> None:
        """Handle menu selection callback."""
        messages = {
            "search": "🔍 ¿Qué tipo de propiedad buscas? Cuéntame sobre tus preferencias "
                      "(habitaciones, ubicación, presupuesto...)",
            "projects": "¿Qué proyectos tienen disponibles?",
            "appointments": "Consulto tus citas agendadas...",
            "agent": "Conectándote con un asesor humano...",
        }
        
        if value in ["projects"]:
            await self.bot.send_chat_action(chat_id, "typing")
            async with get_async_session() as session:
                chat_service = ChatService(session)
                result = await chat_service.process_message(
                    message=messages[value],
                    channel="telegram",
                    channel_user_id=str(user.id),
                )
            await self._send_chat_response(chat_id, result)
        else:
            await self.bot.send_message(chat_id=chat_id, text=messages.get(value, "¿En qué puedo ayudarte?"))
    
    async def _handle_action_callback(
        self,
        chat_id: int,
        value: str,
        user: Any,
    ) -> None:
        """Handle action button callback."""
        if value == "schedule":
            await self.bot.send_message(
                chat_id=chat_id,
                text="📅 ¿Cuándo te gustaría agendar la visita?",
                reply_markup=create_schedule_keyboard(),
            )
        elif value == "more_options":
            await self.bot.send_message(
                chat_id=chat_id,
                text="🔍 Cuéntame más sobre lo que buscas para mostrarte más opciones.",
            )
        elif value == "cancel":
            await self.bot.send_message(
                chat_id=chat_id,
                text="Operación cancelada. ¿En qué más puedo ayudarte?",
            )
    
    async def _handle_confirm_callback(
        self,
        chat_id: int,
        value: str,
        user: Any,
    ) -> None:
        """Handle confirmation callback."""
        if value == "yes":
            await self.bot.send_message(
                chat_id=chat_id,
                text="✅ ¡Confirmado! Te enviaremos los detalles.",
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text="Entendido. ¿En qué más puedo ayudarte?",
            )
    
    async def _send_chat_response(
        self,
        chat_id: int,
        result: Dict[str, Any],
    ) -> None:
        """
        Send formatted chat response to Telegram.
        
        Args:
            chat_id: Target chat ID
            result: Response from chat service
        """
        # Format the response
        text = self.formatter.format_chat_response(result)
        
        # Prepare keyboard if we have properties
        keyboard = None
        properties = result.get("properties")
        if properties and len(properties) > 0:
            keyboard = create_property_keyboard(properties)
        
        suggested_actions = result.get("suggested_actions")
        if suggested_actions and len(suggested_actions) > 0 and not keyboard and result.get("type") == "PROPERTY_SEARCH_RESULT":
            keyboard = create_suggested_actions_keyboard(suggested_actions)
        
        # Send message
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        except Exception as e:
            # If Markdown fails, try without formatting
            logger.warning(f"Markdown failed, sending plain text: {e}")
            await self.bot.send_message(
                chat_id=chat_id,
                text=result.get("response", "Respuesta no disponible"),
                reply_markup=keyboard,
                parse_mode=None,
            )
        
        # If there's an appointment confirmation, send it separately
        """appointment = result.get("appointment")
        if appointment:
            print('Sending appointment: ')
            print(appointment)
            apt_text = self.formatter.format_appointment(appointment)
            print('Appointment text: ')
            print(apt_text)
            await self.bot.send_message(
                chat_id=chat_id,
                text=apt_text,
                parse_mode="MarkdownV2",
            )"""
    
    async def _send_error(self, chat_id: int) -> None:
        """Send error message."""
        await self.bot.send_message(
            chat_id=chat_id,
            text=self.formatter.format_error(),
        )

