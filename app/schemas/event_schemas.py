from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re

class EventCreate(BaseModel):

    title: str = Field(None, example="Sample Event")
    createdby: str = Field(None, example="John Doe")
    startdate: datetime = Field(None, example="2024-12-16")
    enddate: datetime = Field(None, example="2024-12-17")

class EventUpdate(BaseModel):

    title: str = Field(None, example="Sample Event")
    createdby: str = Field(None, example="John Doe")
    startdate: datetime = Field(None, example="2024-12-16")
    enddate: datetime = Field(None, example="2024-12-17")

class EventResponse(BaseModel):
    
    id: uuid.UUID = Field(..., example=uuid.uuid4())
    title: str = Field(None, example="Sample Event")
    createdby: str = Field(None, example="John Doe")
    startdate: datetime = Field(None, example="2024-12-16")
    enddate: datetime = Field(None, example="2024-12-17")

    model_config = {"from_attributes": True}

class EventListResponse(BaseModel):
    items: List[EventResponse] = Field(..., example=[{
        "id": uuid.uuid4(),
        "title": "Sample Event",
        "createdby": "John Doe",
        "startdate": "2024-12-16",
        "enddate": "2024-12-17",
    }])
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)
