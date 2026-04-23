CREATE TABLE IF NOT EXISTS saved_events (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id   UUID REFERENCES users(id) ON DELETE CASCADE,
    event_id  UUID REFERENCES events(id) ON DELETE CASCADE,
    saved_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, event_id)
);
