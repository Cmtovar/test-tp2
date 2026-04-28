from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    start_datetime: datetime
    end_datetime: datetime | None = None
    venue_name: str | None = None
    venue_address: str | None = None
    neighborhood: str | None = None
    lat: float | None = None
    lng: float | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    is_free: bool | None = None
    ticket_url: str | None = None
    source_url: str | None = None
    source: str
    image_url: str | None = None
    status: str | None = None
    tags: list[str] | None = None
    popularity: int | None = None


class EventListResponse(BaseModel):
    data: list[EventOut]
    count: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
