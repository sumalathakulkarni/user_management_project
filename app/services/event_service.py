from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
import secrets
from typing import Optional, Dict, List
from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_email_service, get_settings
from app.models.event_model import Event
from app.schemas.event_schemas import EventCreate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID
from app.services.email_service import EmailService
from app.models.user_model import UserRole
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class EventService:
    @classmethod
    async def create(cls, session: AsyncSession, event_data: Dict[str, str], email_service: EmailService) -> Optional[EventCreate]:
        try:
            validated_data = EventCreate(**event_data).model_dump()
            new_event = Event(**validated_data)
            session.add(new_event)
            await session.commit()
            return new_event
        except ValidationError as e:
            logger.error(f"Validation error during event creation: {e}")
            return None