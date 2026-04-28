"""Abstract base class for event source adapters."""

from abc import ABC, abstractmethod
from datetime import datetime


class EventSourceAdapter(ABC):
    """
    Abstract base class for all event source adapters.
    
    Any adapter (Ticketmaster, SeatGeek, Chicago Parks) must implement
    these methods to plug into the ChiPulse data pipeline.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source identifier (e.g., 'ticketmaster', 'seatgeek')."""
        pass

    @abstractmethod
    def fetch_events(
        self,
        start_date: datetime,
        end_date: datetime,
        location: str,
        **kwargs
    ) -> list[dict]:
        """
        Fetch raw events from the external API.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            location: City/location query (e.g., 'Chicago')
            **kwargs: API-specific parameters (category, radius, etc.)
        
        Returns:
            List of raw event dicts from the API (unconverted)
        """
        pass

    @abstractmethod
    def normalize_event(self, raw_event: dict) -> dict:
        """
        Convert raw API event to ChiPulse standardized format.
        
        Transforms the external API's event format into the schema your
        database expects (see Event model in app/models/event.py).
        
        Args:
            raw_event: Raw event dict from fetch_events()
        
        Returns:
            Normalized event dict with these required fields:
                - source (str): source identifier
                - source_id (str): external event ID
                - title (str): event title
                - start_datetime (datetime): event start
                - Optional: description, category, venue_name, 
                           venue_address, location (lat, lng tuple),
                           price_min, price_max, is_free, ticket_url,
                           source_url, image_url, tags, raw_data
        
        """
        pass

    @abstractmethod
    def validate_event(self, normalized_event: dict) -> bool:
        """
        Validate that a normalized event has all required fields.
        
        Args:
            normalized_event: Output from normalize_event()
        
        Returns:
            True if valid, False otherwise
        """
        pass
