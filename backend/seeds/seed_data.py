"""Execute seeds/seed_events.sql against DATABASE_URL."""
import os
import re
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

SEED_FILE = Path(__file__).parent / "seed_events.sql"


def to_sync_dsn(url: str) -> str:
    return re.sub(r"^postgresql\+asyncpg://", "postgresql://", url)


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set in .env", file=sys.stderr)
        return 1
    if not SEED_FILE.exists():
        print(f"ERROR: seed file not found at {SEED_FILE}", file=sys.stderr)
        return 1

    sql = SEED_FILE.read_text(encoding="utf-8")
    conn = psycopg2.connect(to_sync_dsn(db_url))
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            print(f"Seeding from {SEED_FILE.name}...")
            cur.execute(sql)
            cur.execute("SELECT COUNT(*) FROM events;")
            total = cur.fetchone()[0]
            print(f"OK. Total rows in events table: {total}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
