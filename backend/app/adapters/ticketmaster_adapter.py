"""Ticketmaster Discovery API adapter."""

from datetime import datetime

from app.adapters.base import EventSourceAdapter


class TicketmasterAdapter(EventSourceAdapter):
    """
    Adapter for Ticketmaster Discovery API.
    
    Fetches events from Ticketmaster and normalizes them to ChiPulse format.
    
    Docs: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
    """

    def __init__(self, api_key: str):
        """
        Initialize Ticketmaster adapter.
        
        Args:
            api_key: Ticketmaster Discovery API key
        """
        self.api_key = api_key
        self.base_url = "https://app.ticketmaster.com/discovery/v2"

    @property
    def source_name(self) -> str:
        """Return source identifier."""
        return "ticketmaster"

    def fetch_events(
        self,
        start_date: datetime,
        end_date: datetime,
        location: str,
        **kwargs
    ) -> list[dict]:
        """
        Fetch events from Ticketmaster Discovery API.
        
        TODO (Sprint 3):
            - Implement actual API calls using requests library
            - Handle pagination (API returns max 200 per call)
            - Parse start_date/end_date into Ticketmaster format
            - Pass location to city parameter
            - Handle optional kwargs (category filters, etc.)
            - Implement retry logic for rate limits
        
        Current behavior: Returns empty list (skeleton).
        """
        # TODO: Implement API call
        # Example pseudocode:
        # response = requests.get(
        #     f"{self.base_url}/events.json",
        #     params={
        #         "apikey": self.api_key,
        #         "city": location,
        #         "startDateTime": start_date.isoformat(),
        #         "endDateTime": end_date.isoformat(),
        #         "size": 200
        #     }
        # )
        # return response.json().get("_embedded", {}).get("events", [])
        
        return []

    def normalize_event(self, raw_event: dict) -> dict:
        """
        Convert Ticketmaster event to ChiPulse format.
        
        Maps Ticketmaster's event structure to your database schema.
        
        TODO (Sprint 3):
            - Extract title from raw_event["name"]
            - Extract dates from raw_event["dates"]["start"]
            - Map Ticketmaster classification → your categories
              (Ticketmaster has 100s of categories, map to: 
               music, sports, theater, community, food, arts, family)
            - Extract venue info from raw_event["_embedded"]["venues"][0]
            - Extract lat/lng from venue.location
            - Extract prices from raw_event["priceRanges"]
            - Extract images and URLs
            - Store raw_event in raw_data field
        
        Current behavior: Returns template structure (empty values).
        """
        # TODO: Implement normalization
        # Example structure (placeholder):
        normalized = {
            "source": self.source_name,
            "source_id": None,  # TODO: raw_event.get("id")
            "title": None,  # TODO: raw_event.get("name")
            "description": None,
            "category": None,  # TODO: Map from classifications
            "subcategory": None,
            "start_datetime": None,  # TODO: Parse dates
            "end_datetime": None,
            "venue_name": None,
            "venue_address": None,
            "neighborhood": None,
            "location": None,  # TODO: (lat, lng) tuple
            "price_min": None,
            "price_max": None,
            "is_free": False,
            "ticket_url": None,
            "source_url": None,  # TODO: raw_event.get("url")
            "image_url": None,
            "tags": [],
            "raw_data": raw_event,  # Store original for debugging
        }
        return normalized

    def validate_event(self, normalized_event: dict) -> bool:
        """
        Check that normalized event has required fields.
        
        Required: source, source_id, title, start_datetime
        
        TODO (Sprint 3):
            - Validate required fields exist
            - Validate datetime format
            - Validate location is valid (lat/lng in range)
            - Return False if any validation fails
        
        Current behavior: Validates presence of required fields only.
        """
        required = ["source", "source_id", "title", "start_datetime"]
        return all(normalized_event.get(field) for field in required)
