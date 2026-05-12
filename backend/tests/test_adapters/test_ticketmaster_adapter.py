"""
Tests for TicketmasterAdapter.normalize_event and validate_event.

These tests guard against two categories of breakage:

1. Someone changes the adapter's normalisation logic and silently breaks
   the field mapping that the rest of the app depends on.

2. The Ticketmaster API response changes shape (new/removed keys) and the
   adapter stops producing valid output.

All tests are pure unit tests — no network calls are made.
"""

from datetime import datetime, UTC
from decimal import Decimal

import pytest

from app.adapters.ticketmaster_adapter import TicketmasterAdapter, CATEGORY_MAP


@pytest.fixture
def adapter():
    return TicketmasterAdapter(api_key="fake-key-for-tests")


@pytest.fixture
def full_raw_event():
    """A realistic Ticketmaster API event payload with all common fields populated."""
    return {
        "id": "tm_abc123",
        "name": "Chicago Blues Fest",
        "info": "Annual blues festival in Grant Park.",
        "url": "https://www.ticketmaster.com/event/blues-fest",
        "dates": {
            "start": {"dateTime": "2026-07-04T18:00:00Z"},
            "end": {"dateTime": "2026-07-04T23:00:00Z"},
        },
        "classifications": [
            {
                "segment": {"name": "Music"},
                "genre": {"name": "Blues"},
                "subGenre": {"name": "Chicago Blues"},
            }
        ],
        "priceRanges": [{"min": 15.0, "max": 45.0}],
        "images": [
            {"url": "https://img.example.com/small.jpg", "width": 100, "height": 75},
            {"url": "https://img.example.com/large.jpg", "width": 1024, "height": 768},
        ],
        "_embedded": {
            "venues": [
                {
                    "name": "Grant Park",
                    "address": {"line1": "337 E Randolph St"},
                    "city": {"name": "Chicago"},
                    "state": {"stateCode": "IL"},
                    "location": {"latitude": "41.8827", "longitude": "-87.6233"},
                    "markets": [{"name": "Chicago"}],
                }
            ]
        },
    }


# ---------------------------------------------------------------------------
# source_name
# ---------------------------------------------------------------------------


def test_source_name_is_ticketmaster(adapter):
    assert adapter.source_name == "ticketmaster"


# ---------------------------------------------------------------------------
# normalize_event — required output fields
# ---------------------------------------------------------------------------


def test_normalize_event_returns_all_required_fields(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)

    required = {"id", "title", "source", "start_datetime"}
    for field in required:
        assert field in result, f"normalize_event must return '{field}'"
        assert result[field] is not None, f"'{field}' must not be None"


def test_normalize_event_source_is_always_ticketmaster(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["source"] == "ticketmaster"


def test_normalize_event_maps_title(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["title"] == "Chicago Blues Fest"


def test_normalize_event_maps_start_datetime(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert isinstance(result["start_datetime"], datetime)
    assert result["start_datetime"] == datetime(2026, 7, 4, 18, 0, 0, tzinfo=UTC)


def test_normalize_event_maps_end_datetime(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert isinstance(result["end_datetime"], datetime)


def test_normalize_event_maps_venue_name(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["venue_name"] == "Grant Park"


def test_normalize_event_maps_venue_address(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["venue_address"] is not None
    assert "Chicago" in result["venue_address"]


def test_normalize_event_maps_lat_lng(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert isinstance(result["lat"], float)
    assert isinstance(result["lng"], float)


def test_normalize_event_maps_price_range(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["price_min"] == Decimal("15.0")
    assert result["price_max"] == Decimal("45.0")
    assert result["is_free"] is False


def test_normalize_event_marks_free_when_price_is_zero(adapter, full_raw_event):
    full_raw_event["priceRanges"] = [{"min": 0.0, "max": 0.0}]
    result = adapter.normalize_event(full_raw_event)
    assert result["is_free"] is True


def test_normalize_event_picks_largest_image(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["image_url"] == "https://img.example.com/large.jpg"


def test_normalize_event_maps_category_via_category_map(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    expected_category = CATEGORY_MAP.get("Music")
    assert result["category"] == expected_category


def test_normalize_event_generates_deterministic_uuid(adapter, full_raw_event):
    """The same Ticketmaster ID must always produce the same UUID."""
    result1 = adapter.normalize_event(full_raw_event)
    result2 = adapter.normalize_event(full_raw_event)
    assert result1["id"] == result2["id"]


def test_normalize_event_status_is_active(adapter, full_raw_event):
    result = adapter.normalize_event(full_raw_event)
    assert result["status"] == "active"


# ---------------------------------------------------------------------------
# normalize_event — graceful handling of missing/partial data
# ---------------------------------------------------------------------------


def test_normalize_event_handles_missing_venues(adapter, full_raw_event):
    full_raw_event["_embedded"] = {}
    result = adapter.normalize_event(full_raw_event)
    assert result["venue_name"] is None
    assert result["lat"] is None
    assert result["lng"] is None


def test_normalize_event_handles_missing_price_ranges(adapter, full_raw_event):
    del full_raw_event["priceRanges"]
    result = adapter.normalize_event(full_raw_event)
    assert result["price_min"] is None
    assert result["price_max"] is None
    assert result["is_free"] is None


def test_normalize_event_handles_missing_images(adapter, full_raw_event):
    full_raw_event["images"] = []
    result = adapter.normalize_event(full_raw_event)
    assert result["image_url"] is None


def test_normalize_event_handles_missing_classifications(adapter, full_raw_event):
    full_raw_event["classifications"] = []
    result = adapter.normalize_event(full_raw_event)
    assert result["category"] == "community"
    assert result["subcategory"] is None


def test_normalize_event_handles_missing_end_datetime(adapter, full_raw_event):
    del full_raw_event["dates"]["end"]
    result = adapter.normalize_event(full_raw_event)
    assert result["end_datetime"] is None


def test_normalize_event_falls_back_title_to_untitled(adapter, full_raw_event):
    del full_raw_event["name"]
    result = adapter.normalize_event(full_raw_event)
    assert result["title"] == "Untitled Event"


def test_normalize_event_handles_invalid_lat_lng(adapter, full_raw_event):
    venue = full_raw_event["_embedded"]["venues"][0]
    venue["location"] = {"latitude": "not-a-number", "longitude": "not-a-number"}
    result = adapter.normalize_event(full_raw_event)
    assert result["lat"] is None
    assert result["lng"] is None


# ---------------------------------------------------------------------------
# validate_event
# ---------------------------------------------------------------------------


def test_validate_event_passes_for_valid_normalized_event(adapter, full_raw_event):
    normalized = adapter.normalize_event(full_raw_event)
    assert adapter.validate_event(normalized) is True


def test_validate_event_fails_when_id_is_missing(adapter, full_raw_event):
    normalized = adapter.normalize_event(full_raw_event)
    del normalized["id"]
    assert adapter.validate_event(normalized) is False


def test_validate_event_fails_when_title_is_missing(adapter, full_raw_event):
    normalized = adapter.normalize_event(full_raw_event)
    normalized["title"] = None
    assert adapter.validate_event(normalized) is False


def test_validate_event_fails_when_start_datetime_is_missing(adapter, full_raw_event):
    normalized = adapter.normalize_event(full_raw_event)
    normalized["start_datetime"] = None
    assert adapter.validate_event(normalized) is False


def test_validate_event_fails_when_source_is_missing(adapter, full_raw_event):
    normalized = adapter.normalize_event(full_raw_event)
    normalized["source"] = None
    assert adapter.validate_event(normalized) is False
