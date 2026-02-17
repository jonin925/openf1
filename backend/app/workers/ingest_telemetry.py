import asyncio
from app.services.db import get_pool
from app.services.telemetry_service import TelemetryService

async def main():
    pool = await get_pool()
    telemetry = TelemetryService(pool)
    await telemetry.ingest_all_sessions(2025)  # ingest all 2025 sessions
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
