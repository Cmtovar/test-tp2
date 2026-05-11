import logging
import time
from datetime import date, datetime, time as dtime, timezone
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.adapters.ticketmaster_adapter import TicketmasterAdapter
from app.config import settings
from app.data.mock_events import MOCK_EVENTS
from app.database import db_is_configured, get_session
from app.schemas.event import ErrorDetail, ErrorResponse, EventListResponse, EventOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

CACHE_TTL_SECONDS = 3600
_event_cache: list[EventOut] = []
_cache_timestamp: float = 0.0

ALLOWED_CATEGORIES = {"music", "sports", "theater", "community", "food", "arts", "family"}
ALLOWED_SORTS = {"date", "price", "popularity"}
MILES_TO_METERS = 1609.34
DEFAULT_RADIUS_MILES = 10.0

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
    """Fetch events with 3-tier fallback: cache → API → stale cache → mock."""
    global _event_cache, _cache_timestamp

    cache_age = time.time() - _cache_timestamp
    if _event_cache and cache_age < CACHE_TTL_SECONDS:
        logger.info("Serving %d events from cache (age: %ds)", len(_event_cache), int(cache_age))
        return _event_cache

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

    if _event_cache:
        logger.warning("Serving stale cache (%d events, age: %ds)", len(_event_cache), int(cache_age))
        return _event_cache

    return _get_mock_events()


def _parse_date(value: str | None, field: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format for '{field}'. Expected YYYY-MM-DD.",
        ) from exc


def _validate_filters(
    category: str | None,
    price_max: float | None,
    lat: float | None,
    lng: float | None,
    sort: str,
) -> None:
    if category is not None and category.lower() not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category. Must be one of: {sorted(ALLOWED_CATEGORIES)}",
        )
    if price_max is not None and price_max < 0:
        raise HTTPException(status_code=422, detail="price_max must be >= 0")
    if lat is not None and not -90 <= lat <= 90:
        raise HTTPException(status_code=422, detail="lat must be between -90 and 90")
    if lng is not None and not -180 <= lng <= 180:
        raise HTTPException(status_code=422, detail="lng must be between -180 and 180")
    if sort not in ALLOWED_SORTS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort. Must be one of: {sorted(ALLOWED_SORTS)}",
        )


def _build_db_query(
    *,
    category: str | None,
    date_from: date,
    date_to: date | None,
    is_free: bool | None,
    price_max: float | None,
    lat: float | None,
    lng: float | None,
    radius_miles: float | None,
    q: str | None,
    sort: str,
) -> tuple[str, dict[str, Any]]:
    """Build a parameterized SQL query for events with filters."""
    where: list[str] = []
    params: dict[str, Any] = {}

    where.append("start_datetime >= :date_from")
    params["date_from"] = datetime.combine(date_from, dtime.min, tzinfo=timezone.utc)

    if date_to is not None:
        where.append("start_datetime <= :date_to")
        params["date_to"] = datetime.combine(date_to, dtime.max, tzinfo=timezone.utc)

    if category is not None:
        where.append("LOWER(category) = :category")
        params["category"] = category.lower()

    if is_free is True:
        where.append("is_free = true")

    if price_max is not None:
        where.append("(price_min <= :price_max OR is_free = true)")
        params["price_max"] = price_max

    if lat is not None and lng is not None:
        where.append(
            "location IS NOT NULL AND ST_DWithin("
            "location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)"
        )
        params["lat"] = lat
        params["lng"] = lng
        params["radius_m"] = (radius_miles or DEFAULT_RADIUS_MILES) * MILES_TO_METERS

    if q:
        where.append(
            "(to_tsvector('english', "
            "coalesce(title,'') || ' ' || coalesce(description,'') || ' ' || coalesce(venue_name,''))"
            " @@ plainto_tsquery('english', :q)"
            " OR title ILIKE :q_like OR description ILIKE :q_like OR venue_name ILIKE :q_like)"
        )
        params["q"] = q
        params["q_like"] = f"%{q}%"

    if sort == "price":
        order = "ORDER BY price_min ASC NULLS LAST, start_datetime ASC"
    elif sort == "popularity":
        order = "ORDER BY popularity DESC NULLS LAST, start_datetime ASC"
    else:
        order = "ORDER BY start_datetime ASC"

    where_clause = " WHERE " + " AND ".join(where) if where else ""
    sql = f"SELECT {EVENT_SELECT_COLUMNS} FROM events{where_clause} {order}"
    return sql, params


def _haversine_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    r = 3958.7613
    lat1r, lat2r = radians(lat1), radians(lat2)
    dlat = lat2r - lat1r
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(lat1r) * cos(lat2r) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def _filter_in_memory(
    items: list[EventOut],
    *,
    category: str | None,
    date_from: date,
    date_to: date | None,
    is_free: bool | None,
    price_max: float | None,
    lat: float | None,
    lng: float | None,
    radius_miles: float | None,
    q: str | None,
    sort: str,
) -> list[EventOut]:
    """Apply the same filters in-memory (used when serving from adapter/mock fallback)."""
    df_dt = datetime.combine(date_from, dtime.min, tzinfo=timezone.utc)
    dt_dt = (
        datetime.combine(date_to, dtime.max, tzinfo=timezone.utc) if date_to else None
    )
    q_lower = q.lower() if q else None
    radius_m = (radius_miles or DEFAULT_RADIUS_MILES)

    def keep(ev: EventOut) -> bool:
        start = ev.start_datetime
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if start < df_dt:
            return False
        if dt_dt and start > dt_dt:
            return False
        if category and (ev.category or "").lower() != category.lower():
            return False
        if is_free is True and not ev.is_free:
            return False
        if price_max is not None:
            pm = float(ev.price_min) if ev.price_min is not None else None
            if not (ev.is_free or (pm is not None and pm <= price_max)):
                return False
        if lat is not None and lng is not None:
            if ev.lat is None or ev.lng is None:
                return False
            if _haversine_miles(lat, lng, ev.lat, ev.lng) > radius_m:
                return False
        if q_lower:
            haystack = " ".join(
                filter(None, [ev.title, ev.description, ev.venue_name])
            ).lower()
            if q_lower not in haystack:
                return False
        return True

    filtered = [e for e in items if keep(e)]

    def price_key(e: EventOut) -> tuple[int, Decimal]:
        return (1, Decimal(0)) if e.price_min is None else (0, e.price_min)

    def pop_key(e: EventOut) -> tuple[int, int]:
        return (1, 0) if e.popularity is None else (0, -e.popularity)

    if sort == "price":
        filtered.sort(key=lambda e: (price_key(e), e.start_datetime))
    elif sort == "popularity":
        filtered.sort(key=lambda e: (pop_key(e), e.start_datetime))
    else:
        filtered.sort(key=lambda e: e.start_datetime)
    return filtered


@router.get("", response_model=EventListResponse)
async def list_events(
    category: str | None = Query(None, description="Filter by category (case-insensitive)"),
    date_from: str | None = Query(None, description="Start date filter (YYYY-MM-DD); defaults to today"),
    date_to: str | None = Query(None, description="End date filter (YYYY-MM-DD)"),
    is_free: bool | None = Query(None, description="If true, only free events"),
    price_max: float | None = Query(None, description="Max price (or free events)"),
    lat: float | None = Query(None, description="Center latitude for radius search"),
    lng: float | None = Query(None, description="Center longitude for radius search"),
    radius: float | None = Query(None, description="Radius in miles (default 10 with lat/lng)"),
    q: str | None = Query(None, description="Keyword search across title/description/venue"),
    sort: Literal["date", "price", "popularity"] = Query("date", description="Sort order"),
) -> EventListResponse:
    """List events with optional filters, geo-radius, keyword search, and sorting.

    All filters compose with AND logic. By default only events from today onward are returned.
    """
    parsed_from = _parse_date(date_from, "date_from") or datetime.now(timezone.utc).date()
    parsed_to = _parse_date(date_to, "date_to")
    _validate_filters(category, price_max, lat, lng, sort)

    if (lat is None) != (lng is None):
        raise HTTPException(
            status_code=422,
            detail="lat and lng must be provided together for radius search",
        )
    radius_miles = radius if (lat is not None and lng is not None) else None
    if lat is not None and lng is not None and radius_miles is None:
        radius_miles = DEFAULT_RADIUS_MILES

    filter_kwargs = dict(
        category=category,
        date_from=parsed_from,
        date_to=parsed_to,
        is_free=is_free,
        price_max=price_max,
        lat=lat,
        lng=lng,
        radius_miles=radius_miles,
        q=q,
        sort=sort,
    )

    if db_is_configured():
        try:
            async for s in get_session():
                sql, params = _build_db_query(**filter_kwargs)
                result = await s.execute(text(sql), params)
                rows = result.fetchall()
                items = [_row_to_event(r) for r in rows]
                return EventListResponse(data=items, count=len(items))
        except Exception:
            logger.warning("Database query failed, falling back to Ticketmaster adapter")

    raw_items = _fetch_ticketmaster_events()
    items = _filter_in_memory(raw_items, **filter_kwargs)
    return EventListResponse(data=items, count=len(items))


@router.get(
    "/{event_id}",
    response_model=EventOut,
    responses={404: {"model": ErrorResponse}},
)
async def get_event(event_id: UUID):
    """Get a single event by ID."""
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
