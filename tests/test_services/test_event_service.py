from builtins import range
import pytest
from sqlalchemy import select
from app.dependencies import get_settings
from app.services.event_service import EventService

pytestmark = pytest.mark.asyncio

# Test creating event with valid data
async def test_create_event_with_valid_data(db_session, email_service):

    event_data = {
        "title": "Sample Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    
    event = await EventService.create(db_session, event_data, email_service)
    assert event is not None
    assert event.title == event_data["title"]

# Test creating event with invalid data
async def test_create_event_with_invalid_data(db_session, email_service):

    event_data = {
        "title": "Sample Event",
        "createdby": "John Doe",
        "startdate": "test", #invalid date
        "enddate": "test" #invalid date
    }
    
    event = await EventService.create(db_session, event_data, email_service)
    assert event is None

    
