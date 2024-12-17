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
