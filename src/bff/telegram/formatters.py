"""
Telegram message formatters.
Converts API responses to Telegram-friendly format.
"""
from typing import Dict, Any, List, Optional


class TelegramFormatter:
    """
    Formatter for converting API responses to Telegram messages.
    Uses Markdown formatting for rich text.
    """
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """
        Escape special Markdown characters.
        
        Args:
            text: Text to escape
        
        Returns:
            Escaped text
        """
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    @staticmethod
    def format_property(prop: Dict[str, Any]) -> str:
        """
        Format a single property for Telegram.
        
        Args:
            prop: Property dictionary
        
        Returns:
            Formatted Markdown string
        """
        title = prop.get("title", "Propiedad")
        price = prop.get("price_usd")
        bedrooms = prop.get("bedrooms")
        bathrooms = prop.get("bathrooms")
        district = prop.get("district")
        project = prop.get("project_name")
        area = prop.get("area_m2")
        floor = prop.get("floor")
        
        lines = [f"🏠 *{title}*"]
        
        if project:
            lines.append(f"🏢 Proyecto: {project}")
        
        if district:
            lines.append(f"📍 {district}")
        
        if price:
            lines.append(f"💰 *${price:,}*")
        
        features = []
        if bedrooms is not None:
            features.append(f"🛏 {bedrooms} hab")
        if bathrooms is not None:
            features.append(f"🚿 {bathrooms} baños")
        if area:
            features.append(f"📐 {area} m²")
        if floor:
            features.append(f"🏢 Piso {floor}")
        
        if features:
            lines.append(" | ".join(features))
        
        return "\n".join(lines)
    
    @staticmethod
    def format_properties_list(properties: List[Dict[str, Any]]) -> str:
        """
        Format a list of properties.
        
        Args:
            properties: List of property dictionaries
        
        Returns:
            Formatted Markdown string
        """
        if not properties:
            return "No encontré propiedades con esos criterios. ¿Quieres ajustar la búsqueda?"
        
        lines = [f"🔍 *Encontré {len(properties)} opciones:*\n"]
        
        for i, prop in enumerate(properties[:5], 1):
            lines.append(f"*{i}.* {TelegramFormatter.format_property(prop)}")
            lines.append("")  # Empty line between properties
        
        if len(properties) > 5:
            lines.append(f"_... y {len(properties) - 5} más_")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_appointment(appointment: Dict[str, Any]) -> str:
        """
        Format appointment confirmation.
        
        Args:
            appointment: Appointment dictionary
        
        Returns:
            Formatted Markdown string
        """
        project = appointment.get("project_name", "Proyecto")
        scheduled = appointment.get("scheduled_for", "Por confirmar")
        address = appointment.get("project_address", "")
        
        lines = [
            "✅ *¡Cita Agendada\\!*",
            "",
            f"🏢 *Proyecto:* {project}",
            f"📅 *Fecha:* {scheduled}",
        ]
        
        if address:
            lines.append(f"📍 *Dirección:* {address}")
        
        lines.extend([
            "",
            "_Te contactaremos para confirmar los detalles\\._",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_welcome(user_name: Optional[str] = None) -> str:
        """
        Format welcome message.
        
        Args:
            user_name: User's name
        
        Returns:
            Formatted welcome message
        """
        name = user_name or "!"
        
        return f"""¡Hola {name}! 👋

Soy *Pascal*, tu asistente inmobiliario.

Puedo ayudarte a:
🏠 Buscar departamentos en Lima
📋 Darte información sobre proyectos  
📅 Agendar visitas

¿En qué puedo ayudarte hoy?"""
    
    @staticmethod
    def format_error() -> str:
        """Format error message."""
        return "❌ Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
    
    @staticmethod
    def format_chat_response(response_data: Dict[str, Any]) -> str:
        """
        Format the main chat API response for Telegram.
        
        Args:
            response_data: Response from /api/chat
        
        Returns:
            Formatted message for Telegram
        """
        response_type = response_data.get("type", "")
        response_text = response_data.get("response", "")
        
        # Clean up the response text for Telegram Markdown
        # Replace markdown-style formatting
        formatted = response_text
        
        # Handle bullet points (some LLMs use *)
        lines = formatted.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Convert asterisk lists to bullet emoji
            if line.strip().startswith('* '):
                line = line.replace('* ', '• ', 1)
            elif line.strip().startswith('- '):
                line = line.replace('- ', '• ', 1)
            cleaned_lines.append(line)
        
        formatted = '\n'.join(cleaned_lines)
        
        # Add summary if present
        summary = response_data.get("summary")
        if summary:
            formatted = f"📊 _{summary}_\n\n{formatted}"
        
        return formatted
    
    @staticmethod
    def format_project(project: Dict[str, Any]) -> str:
        """
        Format project details.
        
        Args:
            project: Project dictionary
        
        Returns:
            Formatted Markdown string
        """
        name = project.get("name", "Proyecto")
        district = project.get("district", "")
        description = project.get("description", "")
        address = project.get("address", "")
        has_parking = project.get("includes_parking", False)
        has_showroom = project.get("has_showroom", False)
        
        lines = [f"🏢 *{name}*"]
        
        if district:
            lines.append(f"📍 {district}")
        
        if address:
            lines.append(f"🗺 {address}")
        
        if description:
            lines.append(f"\n_{description}_")
        
        features = []
        if has_parking:
            features.append("🚗 Estacionamiento incluido")
        if has_showroom:
            features.append("🏠 Showroom disponible")
        
        if features:
            lines.append("\n" + "\n".join(features))
        
        return "\n".join(lines)

