from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.event import EventOut


class SaveCreateRequest(BaseModel):
    event_id: UUID


class SaveCreatedResponse(BaseModel):
    event_id: UUID
    saved_at: datetime


class SavedEventEntry(BaseModel):
    event_id: UUID
    saved_at: datetime
    event: EventOut


class SavedEventsListResponse(BaseModel):
    data: list[SavedEventEntry]
    count: int


class SavedCheckResponse(BaseModel):
    is_saved: bool
