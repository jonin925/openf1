import asyncio
from app.services.db import get_pool
from app.services.calendar_service import CalendarService
from app.services.openf1_client import OpenF1Client

async def ingest_full_year(year: int = 2025):
    pool = await get_pool()
    calendar = CalendarService(pool)
    client = OpenF1Client()

    # Step 1: populate races + sessions
    await calendar.ingest_year(year)

    # Step 2: fetch all session keys
    async with pool.acquire() as conn:
        session_rows = await conn.fetch("SELECT session_key FROM sessions")

    # Step 3: ingest telemetry per session
    for row in session_rows:
        sk = row["session_key"]
        telemetry = await client.fetch("location", {"session_key": sk})

        async with pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO telemetry (
                    time, session_key, driver_number,
                    x, y, speed
                )
                VALUES ($1,$2,$3,$4,$5,$6)
                ON CONFLICT DO NOTHING
            """, [
                (
                    t["date"],
                    sk,
                    t["driver_number"],
                    t.get("x"),
                    t.get("y"),
                    t.get("speed"),
                )
                for t in telemetry
            ])

    await pool.close()

if __name__ == "__main__":
    asyncio.run(ingest_full_year(2025))
