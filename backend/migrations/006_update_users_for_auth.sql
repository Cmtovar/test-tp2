-- Add password_hash column to users for local email/password auth (T-22).
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
