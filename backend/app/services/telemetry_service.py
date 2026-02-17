from app.services.openf1_client import OpenF1Client
from datetime import datetime
import asyncio
import httpx

def parse_iso(dt_str):
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

async def fetch_with_retry(client, endpoint, params, retries=5, delay=1):
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

class TelemetryService:
    def __init__(self, pool):
        self.pool = pool
        self.client = OpenF1Client()

    async def ingest_session(self, session_key: int):
        print(f"Fetching telemetry for session {session_key}...")
        telemetry_data = await fetch_with_retry(
            self.client, "telemetry", {"session_key": session_key}
        )

        if not telemetry_data:
            print(f"No telemetry data for session {session_key}")
            return

        batch = []
        for row in telemetry_data:
            batch.append((
                parse_iso(row.get("time")),
                row.get("session_key"),
                row.get("driver_number"),
                row.get("x"),
                row.get("y"),
                row.get("speed"),
                row.get("throttle"),
                row.get("brake"),
                row.get("drs"),
                row.get("gear"),
                row.get("rpm"),
            ))

        async with self.pool.acquire() as conn:
            # Use executemany for batch insert
            await conn.executemany("""
                INSERT INTO telemetry (
                    time, session_key, driver_number, x, y, speed,
                    throttle, brake, drs, gear, rpm
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                ON CONFLICT DO NOTHING
            """, batch)

        print(f"Inserted {len(batch)} rows for session {session_key}")

    async def ingest_all_sessions(self, year: int):
        # Fetch all sessions from DB
        async with self.pool.acquire() as conn:
            sessions = await conn.fetch("""
                SELECT s.session_key, r.race_name, s.session_name
                FROM sessions s
                JOIN races r ON s.race_id = r.race_id
                WHERE r.year = $1
                ORDER BY r.round, s.session_type
            """, year)

        for s in sessions:
            session_key = s["session_key"]
            race_name = s["race_name"]
            session_name = s["session_name"]
            print(f"Starting ingestion for {race_name} - {session_name} (session {session_key})")
            await self.ingest_session(session_key)
            await asyncio.sleep(0.2)  # small delay to reduce API pressure
