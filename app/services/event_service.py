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
from app.schemas.event_schemas import EventCreate, EventUpdate
from uuid import UUID
from app.services.email_service import EmailService
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class EventService:
    
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_event(cls, session: AsyncSession, **filters) -> Optional[Event]:
        query = select(Event).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None
    
    @classmethod
    async def get_by_id(cls, session: AsyncSession, event_id: UUID) -> Optional[Event]:
        return await cls._fetch_event(session, id=event_id)
    
    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of events in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of Events.
        """
        query = select(func.count()).select_from(Event)
        result = await session.execute(query)
        count = result.scalar()
        return count

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
    
    @classmethod
    async def update(cls, session: AsyncSession, event_id: UUID, update_data: Dict[str, str]) -> Optional[EventCreate]:
        try:
            validated_data = EventUpdate(**update_data).model_dump()
            query = update(Event).where(Event.id == event_id).values(**validated_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)
            updated_event = await cls.get_by_id(session, event_id)
            if updated_event:
                session.refresh(updated_event)  # Explicitly refresh the updated ueventser object
                logger.info(f"Event {event_id} updated successfully.")
                return updated_event
            else:
                logger.error(f"Event {event_id} not found after update attempt.")
            return None
        except Exception as e:  # Broad exception handling for debugging
            logger.error(f"Error during event update: {e}")
            return None
        
    @classmethod
    async def delete(cls, session: AsyncSession, event_id: UUID) -> bool:
        event = await cls.get_by_id(session, event_id)
        if not event:
            logger.info(f"Event with ID {event_id} not found.")
            return False
        await session.delete(event)
        await session.commit()
        return True
    
    @classmethod
    async def list_events(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[Event]:
        query = select(Event).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []