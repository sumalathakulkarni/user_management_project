from builtins import str
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user_model import User, UserRole
from app.utils.nickname_gen import generate_nickname
from app.utils.security import hash_password
from app.services.jwt_service import decode_token  # Import your FastAPI app

@pytest.mark.asyncio
async def test_create_event_access_denied(async_client, user_token, email_service):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Define event data for the test
    event_data = {
        "title": "Sample Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_event_invalid_data(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Define event data for the test
    event_data = {
        "title": "Admin Event",
        "createdby": "John Doe",
        "startdate": "Invalid Date",
        "enddate": "Invalid Date"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 422 #Unprocessable Content

@pytest.mark.asyncio
async def test_create_event_as_admin(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Define event data for the test
    event_data = {
        "title": "Admin Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_create_event_as_manager(async_client, admin_user, manager_token):
    headers = {"Authorization": f"Bearer {manager_token}"}
    # Define event data for the test
    event_data = {
        "title": "Manager Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_event(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Define event data for the test
    event_data = {
        "title": "Original Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 200
    create_data = response.json()
    # Validate response schema
    assert "id" in create_data, "Response missing 'id'"

    # Extract the new event's ID
    new_event_id = create_data["id"]
    assert isinstance(new_event_id, str), "Event ID should be a string (UUID)"

    updated_event_data = {
        "title": "Updated Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }

    # Send a POST request to create new event
    response = await async_client.put(f"/events/{new_event_id}", json=updated_event_data, headers=headers)
    
    # Asserts
    assert response.status_code == 200
    updated_data = response.json()
    # Validate response schema
    assert "id" in updated_data, "Response missing 'id'"

    # Extract the new event's ID
    new_event_id = updated_data["id"]
    assert isinstance(new_event_id, str), "Event ID should be a string (UUID)"
    assert updated_data["title"] == updated_event_data["title"]

@pytest.mark.asyncio
async def test_event_delete(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Define event data for the test
    event_data = {
        "title": "New Event",
        "createdby": "John Doe",
        "startdate": "2024-12-17",
        "enddate": "2024-12-17"
    }
    # Send a POST request to create new event
    response = await async_client.post("/events/", json=event_data, headers=headers)
    # Asserts
    assert response.status_code == 200
    create_data = response.json()
    # Validate response schema
    assert "id" in create_data, "Response missing 'id'"

    # Extract the new event's ID
    new_event_id = create_data["id"]
    assert isinstance(new_event_id, str), "Event ID should be a string (UUID)"

    delete_response = await async_client.delete(f"/events/{new_event_id}", headers=headers)
    assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_event_delete_does_not_exist(async_client, admin_token):
    non_existent_event_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID format
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/events/{non_existent_event_id}", headers=headers)
    assert delete_response.status_code == 404