"""
FastAPI router for Telegram webhook.
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import logging
import hashlib
import hmac

from src.config import get_settings
from src.bff.telegram.bot import TelegramBot
from src.bff.telegram.handlers import MessageHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Global bot instance
_bot: Optional[TelegramBot] = None
_handler: Optional[MessageHandler] = None


def get_bot() -> TelegramBot:
    """Get or create bot instance."""
    global _bot
    if _bot is None:
        _bot = TelegramBot()
    return _bot


def get_handler() -> MessageHandler:
    """Get or create handler instance."""
    global _handler
    if _handler is None:
        _handler = MessageHandler(get_bot())
    return _handler


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """
    Webhook endpoint for Telegram Bot API.
    
    Telegram sends updates to this endpoint when users interact with the bot.
    """
    settings = get_settings()
    
    # Verify secret token if configured
    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            logger.warning("Invalid webhook secret token")
            raise HTTPException(status_code=403, detail="Invalid secret token")
    
    try:
        # Parse update
        update = await request.json()
        logger.info(f"Received Telegram update: {update.get('update_id')}")
        
        # Process update
        handler = get_handler()
        await handler.handle_update(update)
        
        # Return 200 OK (Telegram expects this)
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Still return 200 to prevent Telegram from retrying
        return {"ok": True, "error": str(e)}


@router.get("/webhook/info")
async def webhook_info():
    """Get current webhook information."""
    bot = get_bot()
    try:
        info = await bot.get_webhook_info()
        return info
    except Exception as e:
        return {"error": str(e)}


@router.post("/webhook/set")
async def set_webhook(webhook_url: str):
    """
    Set the webhook URL.
    
    Args:
        webhook_url: Full URL for the webhook (must be HTTPS)
    """
    settings = get_settings()
    bot = get_bot()
    
    try:
        result = await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.telegram_webhook_secret,
            allowed_updates=["message", "callback_query"],
        )
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return {"ok": False, "error": str(e)}


@router.delete("/webhook")
async def delete_webhook():
    """Delete the current webhook."""
    bot = get_bot()
    try:
        result = await bot.delete_webhook()
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/bot/me")
async def get_bot_info():
    """Get bot information."""
    bot = get_bot()
    try:
        info = await bot.get_me()
        return info
    except Exception as e:
        return {"error": str(e)}

