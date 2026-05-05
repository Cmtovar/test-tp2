"""Ticketmaster Discovery API adapter."""

import uuid
from datetime import datetime
from decimal import Decimal

import requests

from app.adapters.base import EventSourceAdapter


# Map Ticketmaster segment names to our categories
CATEGORY_MAP = {
    "Music": "music",
    "Sports": "sports",
    "Arts & Theatre": "theater",
    "Film": "arts",
    "Miscellaneous": "community",
    "Undefined": "community",
}


class TicketmasterAdapter(EventSourceAdapter):
    """
    Adapter for Ticketmaster Discovery API.

    Fetches events from Ticketmaster and normalizes them to ChiPulse format.

    Docs: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://app.ticketmaster.com/discovery/v2"

    @property
    def source_name(self) -> str:
        return "ticketmaster"

    def fetch_events(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        location: str = "Chicago",
        **kwargs,
    ) -> list[dict]:
        """Fetch events from Ticketmaster Discovery API."""
        params = {
            "apikey": self.api_key,
            "city": location,
            "stateCode": "IL",
            "size": 50,
            "sort": "date,asc",
        }
        if start_date:
            params["startDateTime"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_date:
            params["endDateTime"] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = requests.get(
            f"{self.base_url}/events.json",
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("_embedded", {}).get("events", [])

    def normalize_event(self, raw_event: dict) -> dict:
        """Convert Ticketmaster event to ChiPulse EventOut format."""
        # Venue info
        venues = raw_event.get("_embedded", {}).get("venues", [])
        venue = venues[0] if venues else {}
        venue_location = venue.get("location", {})

        lat = None
        lng = None
        if venue_location.get("latitude") and venue_location.get("longitude"):
            try:
                lat = float(venue_location["latitude"])
                lng = float(venue_location["longitude"])
            except (ValueError, TypeError):
                pass

        # Address
        address_obj = venue.get("address", {})
        city_obj = venue.get("city", {})
        state_obj = venue.get("state", {})
        address_parts = [
            address_obj.get("line1", ""),
            city_obj.get("name", ""),
            state_obj.get("stateCode", ""),
        ]
        venue_address = ", ".join(p for p in address_parts if p) or None

        # Dates
        dates = raw_event.get("dates", {})
        start_info = dates.get("start", {})
        start_dt_str = start_info.get("dateTime")
        start_datetime = None
        if start_dt_str:
            try:
                start_datetime = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        end_info = dates.get("end", {})
        end_dt_str = end_info.get("dateTime")
        end_datetime = None
        if end_dt_str:
            try:
                end_datetime = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        # Category from classifications
        classifications = raw_event.get("classifications", [])
        classification = classifications[0] if classifications else {}
        segment_name = classification.get("segment", {}).get("name", "")
        genre_name = classification.get("genre", {}).get("name")
        category = CATEGORY_MAP.get(segment_name, "community")
        subcategory = genre_name if genre_name and genre_name != "Undefined" else None

        # Prices
        price_ranges = raw_event.get("priceRanges", [])
        price_min = None
        price_max = None
        is_free = None
        if price_ranges:
            price_min = Decimal(str(price_ranges[0].get("min", 0)))
            price_max = Decimal(str(price_ranges[0].get("max", 0)))
            is_free = price_min == 0 and price_max == 0

        # Image — pick the largest
        images = raw_event.get("images", [])
        image_url = None
        if images:
            best = max(images, key=lambda img: img.get("width", 0) * img.get("height", 0))
            image_url = best.get("url")

        # Tags from genre/subGenre
        tags = []
        if genre_name and genre_name != "Undefined":
            tags.append(genre_name)
        sub_genre = classification.get("subGenre", {}).get("name")
        if sub_genre and sub_genre != "Undefined":
            tags.append(sub_genre)

        # Generate a deterministic UUID from the ticketmaster ID
        source_id = raw_event.get("id", "")
        event_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"ticketmaster:{source_id}")

        return {
            "id": event_uuid,
            "title": raw_event.get("name", "Untitled Event"),
            "description": raw_event.get("info") or raw_event.get("pleaseNote"),
            "category": category,
            "subcategory": subcategory,
            "start_datetime": start_datetime or datetime.now(),
            "end_datetime": end_datetime,
            "venue_name": venue.get("name"),
            "venue_address": venue_address,
            "neighborhood": venue.get("markets", [{}])[0].get("name") if venue.get("markets") else None,
            "lat": lat,
            "lng": lng,
            "price_min": price_min,
            "price_max": price_max,
            "is_free": is_free,
            "ticket_url": raw_event.get("url"),
            "source_url": raw_event.get("url"),
            "source": self.source_name,
            "image_url": image_url,
            "status": "active",
            "tags": tags if tags else None,
            "popularity": None,
        }

    def validate_event(self, normalized_event: dict) -> bool:
        """Check that normalized event has required fields."""
        required = ["id", "title", "start_datetime", "source"]
        return all(normalized_event.get(field) for field in required)
