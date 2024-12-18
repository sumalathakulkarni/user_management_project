from builtins import dict, int, len, str
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_email_service, require_role
from app.schemas.event_schemas import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services.event_service import EventService
from app.dependencies import get_settings
from app.services.email_service import EmailService
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings = get_settings()

@router.get("/events/{event_id}", response_model=EventResponse, name="get_event", tags=["Event Management (Requires Admin or Manager Roles)"])
async def get_event(event_id: UUID, request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Endpoint to fetch an event by its unique identifier (UUID).

    Utilizes the EventService to query the database asynchronously for the event and constructs a response
    model that includes the events's details.

    Args:
        eventr_id: UUID of the event to fetch.
        request: The request object, used to generate full URLs in the response.
        db: Dependency that provides an AsyncSession for database access.
        token: The OAuth2 access token obtained through OAuth2PasswordBearer dependency.
    """
    event = await EventService.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return EventResponse.model_construct(
        id=event.id,
        title=event.title,
        createdby=event.createdby,
        startdate=event.startdate,
        enddate=event.enddate
    )


@router.post("/events/", response_model=EventResponse, tags=["Event Management (Requires Admin or Manager Roles)"])
async def create(event_data: EventCreate, request: Request, db: AsyncSession = Depends(get_db), email_service: EmailService = Depends(get_email_service), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):

    event = await EventService.create(db, event_data.model_dump(), email_service)
    if event:
        return event
    raise HTTPException(status_code=400, detail="event already exists")

@router.put("/events/{event_id}", response_model=EventResponse, name="update_event", tags=["Event Management (Requires Admin or Manager Roles)"])
async def update_event(event_id: UUID, event_update: EventUpdate, request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Update event information.

    - **event_id**: UUID of the event to update.
    - **event_update**: eventUpdate model with updated event information.
    """
    event_data = event_update.model_dump(exclude_unset=True)
    
    updated_event = await EventService.update(db, event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")

    return EventResponse.model_construct(
        id=updated_event.id,
        title=updated_event.title,
        createdby=updated_event.createdby,
        startdate=updated_event.startdate,
        enddate=updated_event.enddate
    )

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_event", tags=["Event Management (Requires Admin or Manager Roles)"])
async def delete_event(event_id: UUID, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Delete a event by its ID.

    - **event_id**: UUID of the event to delete.
    """
    success = await EventService.delete(db, event_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/events/", response_model=EventListResponse, tags=["Event Management (Requires Admin or Manager Roles)"])
async def list_events(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    total_events = await EventService.count(db)
    events = await EventService.list_events(db, skip, limit)
    print(events)
    event_responses = [
        EventResponse.model_validate(event) for event in events
    ]
       
    # Construct the final response with pagination details
    return EventListResponse(
        items=event_responses,
        total=total_events,
        page=skip // limit + 1,
        size=len(event_responses)
    )