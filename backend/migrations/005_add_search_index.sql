-- Full-text search index on events for keyword search across title, description, venue_name.
-- Used by GET /api/events?q=... (T-20).
CREATE INDEX IF NOT EXISTS idx_events_search ON events
USING GIN(to_tsvector('english',
    coalesce(title, '') || ' ' ||
    coalesce(description, '') || ' ' ||
    coalesce(venue_name, '')
));
