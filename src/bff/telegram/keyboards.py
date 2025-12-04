"""
Telegram keyboard builders.
Creates inline keyboards and reply keyboards.
"""
from typing import List, Dict, Any, Optional


class InlineKeyboard:
    """Builder for inline keyboards."""
    
    def __init__(self):
        self.rows: List[List[Dict[str, Any]]] = []
        self.current_row: List[Dict[str, Any]] = []
    
    def add_button(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
    ) -> "InlineKeyboard":
        """
        Add a button to the current row.
        
        Args:
            text: Button text
            callback_data: Data sent on button press
            url: URL to open on button press
        
        Returns:
            Self for chaining
        """
        button = {"text": text}
        
        if callback_data:
            button["callback_data"] = callback_data
        elif url:
            button["url"] = url
        
        self.current_row.append(button)
        return self
    
    def new_row(self) -> "InlineKeyboard":
        """Start a new row of buttons."""
        if self.current_row:
            self.rows.append(self.current_row)
            self.current_row = []
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the inline keyboard markup."""
        if self.current_row:
            self.rows.append(self.current_row)
        
        return {
            "inline_keyboard": self.rows
        }


def create_property_keyboard(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create an inline keyboard with property options.
    
    Args:
        properties: List of property dictionaries
    
    Returns:
        Inline keyboard markup
    """
    keyboard = InlineKeyboard()
    
    for i, prop in enumerate(properties[:5]):  # Max 5 properties
        title = prop.get("title", f"Propiedad {i+1}")
        prop_id = prop.get("id", str(i))
        
        # Truncate title if too long
        if len(title) > 30:
            title = title[:27] + "..."
        
        keyboard.add_button(
            text=f"🏠 {title}",
            callback_data=f"property:{prop_id}",
        )
        keyboard.new_row()
    
    # Add action buttons
    keyboard.add_button(
        text="📅 Agendar visita",
        callback_data="action:schedule",
    )
    keyboard.add_button(
        text="🔍 Más opciones",
        callback_data="action:more_options",
    )
    
    return keyboard.build()

def create_suggested_actions_keyboard(suggested_actions: List[str]) -> Dict[str, Any]:
    """Create keyboard for suggested actions."""
    keyboard = InlineKeyboard()
    
    for action in suggested_actions:
        if action == "agendar_visita":
            keyboard.add_button("📅 Agendar visita", callback_data="action:schedule")
        elif action == "ver_mas_opciones":
            keyboard.add_button("🔍 Más opciones", callback_data="action:more_options")
    
    return keyboard.build()

def create_schedule_time_keyboard() -> Dict[str, Any]:
    """Create keyboard for scheduling time options."""
    keyboard = InlineKeyboard()
    
    keyboard.add_button("🌅 Mañana (10am)", callback_data="time:morning")
    keyboard.add_button("☀️ Tarde (3pm)", callback_data="time:afternoon")
    keyboard.new_row()
    
    return keyboard.build()

def create_schedule_keyboard() -> Dict[str, Any]:
    """Create keyboard for scheduling options."""
    keyboard = InlineKeyboard()
    
    # Day options
    keyboard.add_button("📅 Mañana", callback_data="schedule:tomorrow")
    keyboard.add_button("📅 Pasado mañana", callback_data="schedule:day_after")
    keyboard.new_row()
    
    keyboard.add_button("❌ Cancelar", callback_data="action:cancel")
    
    return keyboard.build()


def create_project_keyboard(projects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create keyboard for project selection."""
    keyboard = InlineKeyboard()
    
    for proj in projects[:5]:
        name = proj.get("name", "Proyecto")
        proj_id = proj.get("id", "")
        
        keyboard.add_button(
            text=f"🏢 {name}",
            callback_data=f"project:{proj_id}",
        )
        keyboard.new_row()
    
    return keyboard.build()


def create_confirmation_keyboard() -> Dict[str, Any]:
    """Create yes/no confirmation keyboard."""
    keyboard = InlineKeyboard()
    
    keyboard.add_button("✅ Sí", callback_data="confirm:yes")
    keyboard.add_button("❌ No", callback_data="confirm:no")
    
    return keyboard.build()


def create_main_menu_keyboard() -> Dict[str, Any]:
    """Create main menu keyboard."""
    keyboard = InlineKeyboard()
    
    keyboard.add_button("🔍 Buscar propiedad", callback_data="menu:search")
    keyboard.new_row()
    keyboard.add_button("🏢 Ver proyectos", callback_data="menu:projects")
    keyboard.new_row()
    keyboard.add_button("📅 Mis citas", callback_data="menu:appointments")
    keyboard.new_row()
    keyboard.add_button("💬 Hablar con asesor", callback_data="menu:agent")
    
    return keyboard.build()

