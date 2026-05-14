import asyncio
import logging
import platform
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from sqlalchemy import text

from app.database import db_is_configured, get_session
from app.routers.events import _fetch_ticketmaster_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{event_id}")
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

    def esc(val: str) -> str:
        return val.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    start_str = fmt_dt(start) or "19700101T000000Z"
    # Default to start + 2h if no end, end equals start, or duration > 24h
    max_duration = timedelta(hours=24)
    use_default_end = (
        end is None
        or fmt_dt(end) == start_str
        or (start is not None and end is not None and hasattr(start, "__sub__") and (end - start) > max_duration)
    )
    if not use_default_end:
        end_str = fmt_dt(end)
    elif start is not None and hasattr(start, "__add__"):
        end_str = fmt_dt(start + timedelta(hours=2))
    else:
        end_str = fmt_dt(start) if start else start_str

    desc_parts = [p for p in [description, source_url] if p]
    desc_text = esc(" - ".join(desc_parts)) if desc_parts else ""

    ics = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ChiPulse//ChiPulse//EN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{event_id}@chipulse",
        f"SUMMARY:{esc(name)}",
        f"DTSTART:{start_str}",
        f"DTEND:{end_str}",
        f"LOCATION:{esc(location)}",
        f"DESCRIPTION:{desc_text}",
        f"URL:{source_url}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ])

    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in name).strip() or "event"
    return Response(
        content=ics.encode("utf-8"),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}.ics"',
        },
    )


@router.get("/{event_id}/apple")
async def export_event_apple(event_id: UUID):
    """Open the .ics export URL in Safari so Apple Calendar handles it natively."""
    if platform.system() != "Darwin":
        raise HTTPException(status_code=400, detail="Apple Calendar export only available on macOS")
    export_url = f"http://127.0.0.1:8000/api/export/{event_id}"
    await asyncio.create_subprocess_exec("open", "-a", "Safari", export_url)
    return {"status": "ok", "message": "Opening in Safari"}
