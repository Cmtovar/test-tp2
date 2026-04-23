CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS events (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source           VARCHAR(50) NOT NULL,
    source_id        VARCHAR(255) NOT NULL,
    title            TEXT NOT NULL,
    description      TEXT,
    category         VARCHAR(100),
    subcategory      VARCHAR(100),
    start_datetime   TIMESTAMPTZ NOT NULL,
    end_datetime     TIMESTAMPTZ,
    venue_name       VARCHAR(255),
    venue_address    TEXT,
    neighborhood     VARCHAR(100),
    location         GEOGRAPHY(POINT, 4326),
    price_min        DECIMAL(10,2),
    price_max        DECIMAL(10,2),
    is_free          BOOLEAN DEFAULT FALSE,
    ticket_url       TEXT,
    source_url       TEXT,
    image_url        TEXT,
    status           VARCHAR(50) DEFAULT 'active',
    tags             TEXT[],
    popularity       INTEGER,
    raw_data         JSONB,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source, source_id)
);
