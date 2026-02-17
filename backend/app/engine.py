# backend/app/engine.py

import asyncio
from typing import List, Dict, Optional

from app.services.db import get_pool
from app.services.calendar_service import CalendarService
from app.services.telemetry_service import TelemetryService
from app.services.openf1_client import OpenF1Client
from app.models.schemas import Session, Lap, Position, TelemetryPoint


class OpenF1Engine:
    """
    Central engine that gathers OpenF1 data (races, sessions, telemetry)
    and exposes methods for frontend/PWA consumption.
    """

    def __init__(self):
        self.pool = None
        self.calendar_service = None
        self.telemetry_service = None
        self.client = OpenF1Client()

    async def initialize(self):
        """Initialize database pool and services"""
        self.pool = await get_pool()
        self.calendar_service = CalendarService(self.pool)
        self.telemetry_service = TelemetryService(self.pool)

    async def ingest_year(self, year: int = 2025, delay: float = 0.2):
        """Ingest races, sessions, and telemetry for a full year"""
        # Step 1: races + sessions
        await self.calendar_service.ingest_year(year, delay_between_calls=delay)

        # Step 2: telemetry
        await self.telemetry_service.ingest_all_sessions(year)

    async def get_sessions(self, year: int = 2025) -> List[Session]:
        """Fetch all sessions for a year from DB"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT s.session_key, r.race_name AS meeting_name,
                       s.session_name, s.date_start
                FROM sessions s
                JOIN races r ON s.race_id = r.race_id
                WHERE r.year = $1
                ORDER BY r.round, s.session_type
            """, year)

        return [Session(
            session_key=row["session_key"],
            meeting_name=row["meeting_name"],
            session_name=row["session_name"],
            date_start=row["date_start"]
        ) for row in rows]

    async def get_laps(self, session_key: int) -> List[Lap]:
        """Fetch laps for a given session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT driver_number, lap_number, lap_time,
                       session_key, date_start
                FROM laps
                WHERE session_key = $1
                ORDER BY driver_number, lap_number
            """, session_key)

        return [Lap(**dict(row)) for row in rows]

    async def get_positions(self, session_key: int) -> List[Position]:
        """Fetch positions for a given session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT driver_number, position, session_key, date
                FROM positions
                WHERE session_key = $1
            """, session_key)

        return [Position(**dict(row)) for row in rows]

    async def get_telemetry(self, session_key: int) -> List[TelemetryPoint]:
        """Fetch telemetry data for a session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT driver_number, speed, x, y, throttle, brake, drs, gear, rpm, time AS date
                FROM telemetry
                WHERE session_key = $1
                ORDER BY time ASC
            """, session_key)

        return [TelemetryPoint(**dict(row)) for row in rows]

    async def close(self):
        """Close DB pool"""
        if self.pool:
            await self.pool.close()

# Example async usage for testing
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    engine = OpenF1Engine()

    @app.on_event("startup")
    async def startup():
        await engine.initialize()
        # Optionally ingest all data on startup
        # await engine.ingest_year(2025)

    @app.on_event("shutdown")
    async def shutdown():
        await engine.close()

    @app.get("/sessions")
    async def sessions(year: int = 2025):
        return await engine.get_sessions(year)

    @app.get("/laps/{session_key}")
    async def laps(session_key: int):
        return await engine.get_laps(session_key)

    @app.get("/positions/{session_key}")
    async def positions(session_key: int):
        return await engine.get_positions(session_key)

    @app.get("/telemetry/{session_key}")
    async def telemetry(session_key: int):
        return await engine.get_telemetry(session_key)

    uvicorn.run(app, host="0.0.0.0", port=8000)
