"""Run SQL migration files in order against DATABASE_URL."""
import os
import re
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def to_sync_dsn(url: str) -> str:
    # Convert SQLAlchemy-style async URL to psycopg2-compatible DSN.
    return re.sub(r"^postgresql\+asyncpg://", "postgresql://", url)


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set in .env", file=sys.stderr)
        return 1

    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print(f"No migration files found in {MIGRATIONS_DIR}")
        return 0

    conn = psycopg2.connect(to_sync_dsn(db_url))
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for path in files:
                print(f"Running migration: {path.name}")
                sql = path.read_text(encoding="utf-8")
                try:
                    cur.execute(sql)
                    print(f"  OK: {path.name}")
                except psycopg2.Error as exc:
                    print(f"  FAILED: {path.name}: {exc}", file=sys.stderr)
                    return 2
    finally:
        conn.close()
    print("All migrations applied successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
