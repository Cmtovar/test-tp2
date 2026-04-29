import logging
import time
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.adapters.ticketmaster_adapter import TicketmasterAdapter
from app.config import settings
from app.data.mock_events import MOCK_EVENTS
from app.database import db_is_configured, get_session
from app.schemas.event import ErrorDetail, ErrorResponse, EventListResponse, EventOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

# In-memory cache for Ticketmaster results (avoids hitting API on every request)
CACHE_TTL_SECONDS = 3600  # 1 hour
_event_cache: list[EventOut] = []
_cache_timestamp: float = 0.0

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


def _get_mock_events() -> list[EventOut]:
    """Last-resort fallback: return hardcoded mock events."""
    logger.warning("All sources failed — serving mock data")
    return [EventOut(**e) for e in MOCK_EVENTS]


def _fetch_ticketmaster_events() -> list[EventOut]:
    """
    Fetch events with 3-tier fallback:
      1. Fresh Ticketmaster API call (if cache expired)
      2. Stale cache (if API call fails but we have old data)
      3. Mock data (if nothing else works)
    """
    global _event_cache, _cache_timestamp

    # Tier 1: serve from fresh cache
    cache_age = time.time() - _cache_timestamp
    if _event_cache and cache_age < CACHE_TTL_SECONDS:
        logger.info("Serving %d events from cache (age: %ds)", len(_event_cache), int(cache_age))
        return _event_cache

    # Tier 1b: try refreshing from Ticketmaster
    if settings.ticketmaster_api_key:
        try:
            logger.info("Cache expired — fetching from Ticketmaster")
            adapter = TicketmasterAdapter(settings.ticketmaster_api_key)
            raw_events = adapter.fetch_events()
            results = []
            for raw in raw_events:
                normalized = adapter.normalize_event(raw)
                if adapter.validate_event(normalized):
                    results.append(EventOut(**normalized))

            if results:
                _event_cache = results
                _cache_timestamp = time.time()
                return results
        except Exception:
            logger.exception("Ticketmaster API call failed")

    # Tier 2: serve stale cache if we have one
    if _event_cache:
        logger.warning("Serving stale cache (%d events, age: %ds)", len(_event_cache), int(cache_age))
        return _event_cache

    # Tier 3: mock data
    return _get_mock_events()


@router.get("", response_model=EventListResponse)
async def list_events():
    # Try database first if configured
    if db_is_configured():
        try:
            async for s in get_session():
                query = text(f"SELECT {EVENT_SELECT_COLUMNS} FROM events ORDER BY start_datetime ASC")
                result = await s.execute(query)
                rows = result.fetchall()
                items = [_row_to_event(r) for r in rows]
                return EventListResponse(data=items, count=len(items))
        except Exception:
            logger.warning("Database query failed, falling back to Ticketmaster adapter")

    # Fallback: Ticketmaster → stale cache → mock data
    items = _fetch_ticketmaster_events()
    return EventListResponse(data=items, count=len(items))


@router.get(
    "/{event_id}",
    response_model=EventOut,
    responses={404: {"model": ErrorResponse}},
)
async def get_event(event_id: UUID):
    # Try database first if configured
    if db_is_configured():
        try:
            async for s in get_session():
                query = text(f"SELECT {EVENT_SELECT_COLUMNS} FROM events WHERE id = :id")
                result = await s.execute(query, {"id": str(event_id)})
                row = result.fetchone()
                if row is not None:
                    return _row_to_event(row)
        except Exception:
            logger.warning("Database query failed, falling back to Ticketmaster adapter")

    # Fallback: search cached/fetched events for matching ID
    items = _fetch_ticketmaster_events()
    for item in items:
        if item.id == event_id:
            return item

    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error=ErrorDetail(code="NOT_FOUND", message="Event not found")
        ).model_dump(),
    )
