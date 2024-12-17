from builtins import bool, int, str
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, func, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Event(Base):
    """
    Represents a user within the application, corresponding to the 'users' table in the database.
    This class uses SQLAlchemy ORM for mapping attributes to database columns efficiently.
    
    Attributes:
        id (UUID): Unique identifier for the user.
        title (str): Event Name, required.
        createdby (str): Created by user, required.
        startdate (datetime): Event start date.
        enddate (datetime): Event end date.
        created_at (datetime): Timestamp when the user was created, set by the server.
        updated_at (datetime): Timestamp of the last update, set by the server.

    Methods:
        lock_account(): Locks the user account.
        unlock_account(): Unlocks the user account.
        verify_email(): Marks the user's email as verified.
        has_role(role_name): Checks if the user has a specified role.
        update_professional_status(status): Updates the professional status and logs the update time.
    """
    __tablename__ = "events"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    createdby: Mapped[str] = Column(String(100), nullable=True)
    startdate: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    enddate: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    