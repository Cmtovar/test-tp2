CREATE TABLE IF NOT EXISTS users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email          VARCHAR(255) UNIQUE NOT NULL,
    display_name   VARCHAR(100),
    auth_provider  VARCHAR(50),
    auth_id        VARCHAR(255) UNIQUE,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
