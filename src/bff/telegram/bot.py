"""
Telegram Bot client.
Handles communication with Telegram Bot API.
"""
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.config import get_settings


@dataclass
class TelegramUser:
    """Telegram user data."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


@dataclass
class TelegramMessage:
    """Telegram message data."""
    message_id: int
    chat_id: int
    user: TelegramUser
    text: Optional[str] = None
    date: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelegramMessage":
        """Create from Telegram API response."""
        user_data = data.get("from", {})
        user = TelegramUser(
            id=user_data.get("id"),
            first_name=user_data.get("first_name", "Usuario"),
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            language_code=user_data.get("language_code"),
        )
        
        return cls(
            message_id=data.get("message_id"),
            chat_id=data.get("chat", {}).get("id"),
            user=user,
            text=data.get("text"),
            date=data.get("date"),
        )


@dataclass
class CallbackQuery:
    """Telegram callback query from inline keyboard."""
    id: str
    chat_id: int
    message_id: int
    user: TelegramUser
    data: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallbackQuery":
        """Create from Telegram API response."""
        user_data = data.get("from", {})
        user = TelegramUser(
            id=user_data.get("id"),
            first_name=user_data.get("first_name", "Usuario"),
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            language_code=user_data.get("language_code"),
        )
        
        message = data.get("message", {})
        
        return cls(
            id=data.get("id"),
            chat_id=message.get("chat", {}).get("id"),
            message_id=message.get("message_id"),
            user=user,
            data=data.get("data", ""),
        )


class TelegramBot:
    """
    Telegram Bot API client.
    Handles sending messages and managing bot interactions.
    """
    
    BASE_URL = "https://api.telegram.org/bot{token}/{method}"
    
    def __init__(self, token: Optional[str] = None):
        settings = get_settings()
        self.token = token or settings.telegram_bot_token
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_url(self, method: str) -> str:
        """Get full API URL for a method."""
        return self.BASE_URL.format(token=self.token, method=method)
    
    async def _request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Telegram API."""
        url = self._get_url(method)
        response = await self.client.post(url, json=data)
        result = response.json()
        
        if not result.get("ok"):
            error = result.get("description", "Unknown error")
            raise Exception(f"Telegram API error: {error}")
        
        return result.get("result", {})
    
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        return await self._request("getMe", {})
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict] = None,
        disable_web_page_preview: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a text message.
        
        Args:
            chat_id: Target chat ID
            text: Message text (supports Markdown)
            parse_mode: Parse mode (Markdown, HTML, or None)
            reply_markup: Optional inline keyboard or reply keyboard
            disable_web_page_preview: Disable link previews
        
        Returns:
            Sent message data
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        return await self._request("sendMessage", data)
    
    async def send_chat_action(
        self,
        chat_id: int,
        action: str = "typing",
    ) -> bool:
        """
        Send a chat action (typing indicator).
        
        Args:
            chat_id: Target chat ID
            action: Action type (typing, upload_photo, etc.)
        
        Returns:
            True on success
        """
        data = {
            "chat_id": chat_id,
            "action": action,
        }
        
        return await self._request("sendChatAction", data)
    
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
    ) -> bool:
        """
        Answer a callback query from inline keyboard.
        
        Args:
            callback_query_id: Query ID
            text: Optional notification text
            show_alert: Show as alert instead of notification
        
        Returns:
            True on success
        """
        data = {
            "callback_query_id": callback_query_id,
        }
        
        if text:
            data["text"] = text
            data["show_alert"] = show_alert
        
        return await self._request("answerCallbackQuery", data)
    
    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Edit a message text.
        
        Args:
            chat_id: Chat ID
            message_id: Message to edit
            text: New text
            parse_mode: Parse mode
            reply_markup: New inline keyboard
        
        Returns:
            Edited message data
        """
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        return await self._request("editMessageText", data)
    
    async def set_webhook(
        self,
        url: str,
        secret_token: Optional[str] = None,
        allowed_updates: Optional[List[str]] = None,
    ) -> bool:
        """
        Set webhook URL for receiving updates.
        
        Args:
            url: Webhook URL (HTTPS required)
            secret_token: Optional secret for verification
            allowed_updates: List of update types to receive
        
        Returns:
            True on success
        """
        data = {
            "url": url,
        }
        
        if secret_token:
            data["secret_token"] = secret_token
        
        if allowed_updates:
            data["allowed_updates"] = allowed_updates
        
        return await self._request("setWebhook", data)
    
    async def delete_webhook(self) -> bool:
        """Delete the current webhook."""
        return await self._request("deleteWebhook", {})
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook status."""
        return await self._request("getWebhookInfo", {})

