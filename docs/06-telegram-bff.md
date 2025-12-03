# Fase 6: Telegram BFF (Backend for Frontend)

## 📋 Objetivo

Crear una capa externa (BFF) que conecte la API de Telegram con el core del sistema. Esta arquitectura permite:
- Desacoplar la lógica de negocio de las integraciones externas
- Facilitar futuras integraciones (WhatsApp, Instagram, etc.)
- Mantener el core agnóstico del canal de comunicación

---

## ✅ Checklist

### 6.1 Bot de Telegram
- [ ] Configurar python-telegram-bot
- [ ] Webhook o polling para recibir mensajes
- [ ] Handler de mensajes de texto
- [ ] Handler de comandos (/start, /help)

### 6.2 Integración con Core API
- [ ] Cliente HTTP para llamar al core
- [ ] Mapeo de Telegram chat_id → lead
- [ ] Transformación de respuestas estructuradas → texto Telegram

### 6.3 Formateo de Mensajes
- [ ] Markdown para Telegram
- [ ] Botones inline para acciones
- [ ] Formateo de propiedades
- [ ] Manejo de imágenes (opcional)

### 6.4 Manejo de Estado
- [ ] Persistencia de chat_id en leads
- [ ] Creación automática de leads nuevos
- [ ] Contexto de conversación

---

## 📁 Estructura de Archivos

```
bff/
├── telegram/
│   ├── __init__.py
│   ├── main.py              # Entry point del bot
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py      # /start, /help
│   │   └── messages.py      # Mensajes de texto
│   ├── services/
│   │   ├── __init__.py
│   │   ├── core_client.py   # Cliente para Core API
│   │   └── formatter.py     # Formateo de mensajes
│   └── config.py            # Configuración del BFF
```

---

## 🏗️ Arquitectura BFF

```
┌─────────────────┐
│  Telegram API   │
└────────┬────────┘
         │ Webhook/Polling
         ▼
┌─────────────────────────────────────────┐
│           TELEGRAM BFF                   │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌────────────────┐  │
│  │  Handlers   │───▶│  Core Client   │  │
│  └─────────────┘    └───────┬────────┘  │
│         │                   │           │
│         ▼                   │           │
│  ┌─────────────┐            │           │
│  │  Formatter  │◀───────────┘           │
│  └─────────────┘                        │
└─────────────────────────────────────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│    CORE API     │
│   (FastAPI)     │
└─────────────────┘
```

---

## 🔧 Implementación

### Main Bot

```python
# bff/telegram/main.py
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bff.telegram.config import get_telegram_settings
from bff.telegram.handlers.commands import start_command, help_command
from bff.telegram.handlers.messages import handle_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

settings = get_telegram_settings()

def main():
    """Start the bot."""
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

### Command Handlers

```python
# bff/telegram/handlers/commands.py
from telegram import Update
from telegram.ext import ContextTypes

WELCOME_MESSAGE = """
🏠 *¡Bienvenido a Pascal Real Estate!*

Soy tu asistente virtual y puedo ayudarte a:

• 🔍 Buscar departamentos y propiedades
• 📋 Darte información sobre proyectos
• 📅 Agendar visitas

Solo escríbeme lo que necesitas. Por ejemplo:
- "Busco un depa de 2 habitaciones en Miraflores"
- "Quiero información sobre el proyecto Torre Pacífico"
- "Quisiera agendar una visita"

¿En qué puedo ayudarte hoy?
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
*Comandos disponibles:*

/start - Iniciar conversación
/help - Ver esta ayuda

*¿Qué puedo hacer?*

Puedo ayudarte a encontrar tu departamento ideal. Solo dime qué buscas:
- Número de habitaciones
- Distrito o zona
- Rango de precio
- Características especiales

También puedo agendar visitas a los proyectos que te interesen.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')
```

### Message Handler

```python
# bff/telegram/handlers/messages.py
from telegram import Update
from telegram.ext import ContextTypes

from bff.telegram.services.core_client import CoreAPIClient
from bff.telegram.services.formatter import TelegramFormatter

core_client = CoreAPIClient()
formatter = TelegramFormatter()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    chat_id = str(update.effective_chat.id)
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    # Show typing indicator
    await update.effective_chat.send_action("typing")
    
    try:
        # Call Core API
        response = await core_client.send_message(
            message=user_message,
            telegram_chat_id=chat_id,
            user_name=user_name
        )
        
        # Format response for Telegram
        formatted = formatter.format_response(response)
        
        # Send response
        await update.message.reply_text(
            formatted.text,
            parse_mode='Markdown',
            reply_markup=formatted.reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(
            "Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo."
        )
```

### Core API Client

```python
# bff/telegram/services/core_client.py
import httpx
from bff.telegram.config import get_telegram_settings

settings = get_telegram_settings()

class CoreAPIClient:
    """Client to communicate with Core API."""
    
    def __init__(self):
        self.base_url = settings.core_api_url
    
    async def send_message(
        self,
        message: str,
        telegram_chat_id: str,
        user_name: str | None = None
    ) -> dict:
        """Send message to Core API and get response."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": message,
                    "channel": "telegram",
                    "channel_user_id": telegram_chat_id,
                    "user_name": user_name
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

### Message Formatter

```python
# bff/telegram/services/formatter.py
from dataclasses import dataclass
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

@dataclass
class FormattedMessage:
    text: str
    reply_markup: InlineKeyboardMarkup | None = None

class TelegramFormatter:
    """Format Core API responses for Telegram."""
    
    def format_response(self, response: dict) -> FormattedMessage:
        """Format structured response for Telegram."""
        response_type = response.get("type", "GENERAL")
        
        if response_type == "PROPERTY_SEARCH_RESULT":
            return self._format_property_search(response)
        elif response_type == "SCHEDULE_CONFIRMATION":
            return self._format_schedule_confirmation(response)
        else:
            return FormattedMessage(text=response.get("response", ""))
    
    def _format_property_search(self, response: dict) -> FormattedMessage:
        """Format property search results."""
        text_parts = [response.get("response", "")]
        
        properties = response.get("properties", [])
        if properties:
            text_parts.append("\n*Propiedades encontradas:*\n")
            
            for i, prop in enumerate(properties[:5], 1):
                text_parts.append(
                    f"{i}. *{prop['title']}*\n"
                    f"   📍 {prop.get('district', 'N/A')} - {prop.get('project_name', '')}\n"
                    f"   🛏️ {prop.get('bedrooms', 'N/A')} hab\n"
                    f"   💰 ${prop.get('price_usd', 0):,}\n"
                )
        
        # Add action buttons
        buttons = []
        if properties:
            buttons.append([
                InlineKeyboardButton("📅 Agendar visita", callback_data="schedule_visit")
            ])
        
        return FormattedMessage(
            text="\n".join(text_parts),
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
    
    def _format_schedule_confirmation(self, response: dict) -> FormattedMessage:
        """Format schedule confirmation."""
        appointment = response.get("appointment", {})
        
        text = f"""
✅ *¡Cita agendada exitosamente!*

📅 Fecha: {appointment.get('scheduled_for', 'Por confirmar')}
🏢 Proyecto: {appointment.get('project_name', 'N/A')}

Te contactaremos para confirmar los detalles.
"""
        return FormattedMessage(text=text)
```

---

## ⚙️ Configuración

```python
# bff/telegram/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class TelegramBFFSettings(BaseSettings):
    telegram_bot_token: str
    core_api_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_telegram_settings() -> TelegramBFFSettings:
    return TelegramBFFSettings()
```

---

## 🧪 Verificación

```bash
# 1. Asegurarse que Core API está corriendo
curl http://localhost:8000/health

# 2. Iniciar el bot de Telegram
python -m bff.telegram.main

# 3. Probar en Telegram:
#    - Buscar el bot por su username
#    - Enviar /start
#    - Probar conversaciones
```

---

## 🚀 Despliegue

### Opción A: Polling (desarrollo)
```bash
python -m bff.telegram.main
```

### Opción B: Webhook (producción)
```python
# Configurar webhook
await application.bot.set_webhook(
    url=f"https://your-domain.com/webhook/{settings.telegram_bot_token}"
)
```

---

## 📚 Referencias

- [python-telegram-bot](https://python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BFF Pattern](https://samnewman.io/patterns/architectural/bff/)

