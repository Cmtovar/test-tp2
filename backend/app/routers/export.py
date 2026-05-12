import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from app.database import db_is_configured, get_session
from app.routers.events import _fetch_ticketmaster_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{event_id}", response_class=PlainTextResponse)
async def export_event_ics(event_id: UUID):
    """Export a single event as a .ics calendar file."""

    event = None

    # Try database first
    if db_is_configured():
        try:
            async for s in get_session():
                result = await s.execute(
                    text("SELECT * FROM events WHERE id = :id"),
                    {"id": str(event_id)}
                )
                row = result.fetchone()
                if row:
                    event = dict(row._mapping)
        except Exception:
            logger.warning("DB lookup failed for export, falling back to cache")

    # Fall back to in-memory cache
    if event is None:
        items = _fetch_ticketmaster_events()
        for item in items:
            if item.id == event_id:
                event = item.model_dump()
                break

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Build .ics content
    start = event.get("start_datetime")
    end = event.get("end_datetime")
    name = event.get("title") or event.get("name") or "Event"
    location = event.get("venue_address") or event.get("address") or ""
    description = event.get("description") or ""
    source_url = event.get("source_url") or event.get("ticket_url") or ""

    def fmt_dt(dt):
        if dt is None:
            return None
        if hasattr(dt, "strftime"):
            return dt.strftime("%Y%m%dT%H%M%SZ")
        return str(dt).replace("-", "").replace(":", "").replace(" ", "T")[:15] + "Z"

    start_str = fmt_dt(start) or "19700101T000000Z"
    end_str = fmt_dt(end) or start_str

    ics = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ChiPulse//ChiPulse//EN",
        "BEGIN:VEVENT",
        f"UID:{event_id}@chipulse",
        f"SUMMARY:{name}",
        f"DTSTART:{start_str}",
        f"DTEND:{end_str}",
        f"LOCATION:{location}",
        f"DESCRIPTION:{description} {source_url}".strip(),
        f"URL:{source_url}",
        "END:VEVENT",
        "END:VCALENDAR",
    ])

    return PlainTextResponse(
        content=ics,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="event-{event_id}.ics"'
        }
    )
