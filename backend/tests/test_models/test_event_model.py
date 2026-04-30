from datetime import UTC, datetime
from uuid import uuid4

from app.models.event import Event


def test_event_model_table_name():
    assert Event.__tablename__ == "events"


def test_event_model_accepts_required_fields():
    event_id = uuid4()
    start = datetime(2026, 5, 1, 18, 0, tzinfo=UTC)

    event = Event(
        id=event_id,
        source="ticketmaster",
        source_id="tm_12345",
        title="Concert in Grant Park",
        start_datetime=start,
    )

    assert event.id == event_id
    assert event.source == "ticketmaster"
    assert event.source_id == "tm_12345"
    assert event.title == "Concert in Grant Park"
    assert event.start_datetime == start
