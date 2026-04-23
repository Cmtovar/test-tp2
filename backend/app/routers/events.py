from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.event import ErrorDetail, ErrorResponse, EventListResponse, EventOut

router = APIRouter(prefix="/api/events", tags=["events"])

EVENT_SELECT_COLUMNS = """
    id, title, description, category, subcategory,
    start_datetime, end_datetime,
    venue_name, venue_address, neighborhood,
    CASE WHEN location IS NOT NULL THEN ST_Y(location::geometry) END AS lat,
    CASE WHEN location IS NOT NULL THEN ST_X(location::geometry) END AS lng,
    price_min, price_max, is_free,
    ticket_url, source_url, source, image_url,
    status, tags, popularity
"""


def _row_to_event(row) -> EventOut:
    return EventOut(**dict(row._mapping))


@router.get("", response_model=EventListResponse)
async def list_events(session: AsyncSession = Depends(get_session)) -> EventListResponse:
    query = text(f"SELECT {EVENT_SELECT_COLUMNS} FROM events ORDER BY start_datetime ASC")
    result = await session.execute(query)
    rows = result.fetchall()
    items = [_row_to_event(r) for r in rows]
    return EventListResponse(data=items, count=len(items))


@router.get(
    "/{event_id}",
    response_model=EventOut,
    responses={404: {"model": ErrorResponse}},
)
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_session)):
    query = text(f"SELECT {EVENT_SELECT_COLUMNS} FROM events WHERE id = :id")
    result = await session.execute(query, {"id": str(event_id)})
    row = result.fetchone()
    if row is None:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error=ErrorDetail(code="NOT_FOUND", message="Event not found")
            ).model_dump(),
        )
    return _row_to_event(row)
