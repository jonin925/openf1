from app.services.openf1_client import OpenF1Client
from datetime import datetime
import asyncio
import httpx

def parse_iso(dt_str):
    """Convert ISO string to datetime object for asyncpg TIMESTAMPTZ columns."""
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

async def fetch_with_retry(client, endpoint, params, retries=5, delay=1):
    """Fetch from API with exponential backoff on 429 errors."""
    for attempt in range(retries):
        try:
            resp = await client.fetch(endpoint, params)
            return resp
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = delay * (2 ** attempt)
                print(f"[429] Rate limited. Waiting {wait}s before retrying {endpoint}...")
                await asyncio.sleep(wait)
            else:
                raise
    raise Exception(f"Failed to fetch {endpoint} after {retries} retries due to 429")

class CalendarService:
    def __init__(self, pool):
        self.pool = pool
        self.client = OpenF1Client()

    async def ingest_year(self, year: int, delay_between_calls: float = 0.5):
        """Ingest all races and sessions for a given year."""
        # Fetch all races for the year
        races = await fetch_with_retry(self.client, "meetings", {"year": year})

        async with self.pool.acquire() as conn:
            for r in races:
                # Parse race start/end datetime
                start_dt = parse_iso(r.get("date_start"))
                end_dt = parse_iso(r.get("date_end"))

                # Insert race
                race_id = await conn.fetchval("""
                    INSERT INTO public.races (
                        year, round, circuit_short_name, country, race_name, date_start, date_end
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7)
                    ON CONFLICT DO NOTHING
                    RETURNING race_id
                """,
                    year,
                    r.get("meeting_key"),
                    r.get("circuit_short_name"),
                    r.get("country_name"),
                    r.get("meeting_name"),
                    start_dt,
                    end_dt,
                )

                # Sometimes ON CONFLICT returns None, fetch manually
                if race_id is None:
                    race_id = await conn.fetchval("""
                        SELECT race_id FROM public.races WHERE year=$1 AND round=$2
                    """, year, r.get("meeting_key"))

                # Fetch sessions for this race
                sessions = await fetch_with_retry(self.client, "sessions", {"meeting_key": r["meeting_key"]})

                # Insert sessions
                for s in sessions:
                    s_start = parse_iso(s.get("date_start"))
                    s_end = parse_iso(s.get("date_end"))
                    await conn.execute("""
                        INSERT INTO public.sessions (
                            session_key, race_id, session_type, session_name, date_start, date_end
                        ) VALUES ($1,$2,$3,$4,$5,$6)
                        ON CONFLICT (session_key) DO NOTHING
                    """,
                        s["session_key"],
                        race_id,
                        s.get("session_type"),
                        s.get("session_name"),
                        s_start,
                        s_end,
                    )

                # Optional delay between races to reduce API pressure
                await asyncio.sleep(delay_between_calls)


# Example usage
if __name__ == "__main__":
    import os
    import asyncpg

    async def main():
        # Adjust DSN as per your f1db config
        pool = await asyncpg.create_pool(
            dsn=os.getenv("POSTGRES_DSN", "postgresql://f1user:strongpassword@localhost:5432/f1db"),
            min_size=1,
            max_size=5
        )
        service = CalendarService(pool)
        await service.ingest_year(2025)
        await pool.close()

    asyncio.run(main())
