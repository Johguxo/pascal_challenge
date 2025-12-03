"""
Database repositories for all entities.
"""
from src.database.repositories.base import BaseRepository
from src.database.repositories.leads import LeadRepository
from src.database.repositories.conversations import ConversationRepository
from src.database.repositories.messages import MessageRepository
from src.database.repositories.projects import ProjectRepository
from src.database.repositories.properties import PropertyRepository
from src.database.repositories.typologies import TypologyRepository
from src.database.repositories.appointments import AppointmentRepository

__all__ = [
    "BaseRepository",
    "LeadRepository",
    "ConversationRepository",
    "MessageRepository",
    "ProjectRepository",
    "PropertyRepository",
    "TypologyRepository",
    "AppointmentRepository",
]
