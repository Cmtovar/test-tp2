"""Saved-event endpoints: save, list, unsave, check (all auth-required)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_session
from app.schemas.event import EventOut
from app.schemas.save import (
    SaveCreatedResponse,
    SaveCreateRequest,
    SavedCheckResponse,
    SavedEventEntry,
    SavedEventsListResponse,
)

router = APIRouter(prefix="/api/saves", tags=["saves"])

EVENT_SELECT_COLUMNS = """
    e.id, e.title, e.description, e.category, e.subcategory,
    e.start_datetime, e.end_datetime,
    e.venue_name, e.venue_address, e.neighborhood,
    CASE WHEN e.location IS NOT NULL THEN ST_Y(e.location::geometry) END AS lat,
    CASE WHEN e.location IS NOT NULL THEN ST_X(e.location::geometry) END AS lng,
    e.price_min, e.price_max, e.is_free,
    e.ticket_url, e.source_url, e.source, e.image_url,
    e.status, e.tags, e.popularity
"""


@router.post("", response_model=SaveCreatedResponse, status_code=status.HTTP_201_CREATED)
async def save_event(
    body: SaveCreateRequest,
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SaveCreatedResponse:
    """Mark an event as saved for the current user."""
    event_row = await session.execute(
        text("SELECT id FROM events WHERE id = :id"),
        {"id": str(body.event_id)},
    )
    if event_row.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    existing = await session.execute(
        text("SELECT id FROM saved_events WHERE user_id = :uid AND event_id = :eid"),
        {"uid": str(user_id), "eid": str(body.event_id)},
    )
    if existing.fetchone() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Event already saved")

    result = await session.execute(
        text(
            "INSERT INTO saved_events (user_id, event_id) "
            "VALUES (:uid, :eid) RETURNING event_id, saved_at"
        ),
        {"uid": str(user_id), "eid": str(body.event_id)},
    )
    row = result.fetchone()
    await session.commit()
    return SaveCreatedResponse(event_id=row._mapping["event_id"], saved_at=row._mapping["saved_at"])


@router.get("", response_model=SavedEventsListResponse)
async def list_saves(
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SavedEventsListResponse:
    """List all saved events for the current user, newest first, with full event data."""
    query = text(
        f"SELECT s.event_id, s.saved_at, {EVENT_SELECT_COLUMNS} "
        "FROM saved_events s JOIN events e ON e.id = s.event_id "
        "WHERE s.user_id = :uid "
        "ORDER BY s.saved_at DESC"
    )
    result = await session.execute(query, {"uid": str(user_id)})
    rows = result.fetchall()

    entries: list[SavedEventEntry] = []
    for r in rows:
        m = dict(r._mapping)
        event_data = {k: m[k] for k in EventOut.model_fields.keys() if k in m}
        entries.append(
            SavedEventEntry(
                event_id=m["event_id"],
                saved_at=m["saved_at"],
                event=EventOut(**event_data),
            )
        )
    return SavedEventsListResponse(data=entries, count=len(entries))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_event(
    event_id: UUID,
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Remove a saved event for the current user."""
    result = await session.execute(
        text(
            "DELETE FROM saved_events WHERE user_id = :uid AND event_id = :eid RETURNING id"
        ),
        {"uid": str(user_id), "eid": str(event_id)},
    )
    if result.fetchone() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved event not found"
        )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/check/{event_id}", response_model=SavedCheckResponse)
async def check_saved(
    event_id: UUID,
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SavedCheckResponse:
    """Return whether the current user has saved this event."""
    result = await session.execute(
        text("SELECT 1 FROM saved_events WHERE user_id = :uid AND event_id = :eid"),
        {"uid": str(user_id), "eid": str(event_id)},
    )
    return SavedCheckResponse(is_saved=result.fetchone() is not None)
