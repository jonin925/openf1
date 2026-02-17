import httpx
from typing import Any, Dict, List

BASE_URL = "https://api.openf1.org/v1"

class OpenF1Client:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)

    async def fetch(self, endpoint: str, params: Dict[str, Any] | None = None) -> List[Dict]:
        url = f"{BASE_URL}/{endpoint}"
        resp = await self.client.get(url, params=params)

        # Gracefully handle endpoints that don't exist for a session
        if resp.status_code == 422:
            return []

        resp.raise_for_status()
        return resp.json()

    async def get_sessions_2025(self):
        return await self.fetch("sessions", {"year": 2025})

    async def get_laps(self, session_key: int):
        return await self.fetch("laps", {"session_key": session_key})

    async def get_positions(self, session_key: int):
        return await self.fetch("position", {"session_key": session_key})

    async def get_stints(self, session_key: int):
        return await self.fetch("stints", {"session_key": session_key})

    async def get_telemetry(self, session_key: int):
        # Some sessions have no location telemetry
        data = await self.fetch("location", {"session_key": session_key})
        if not data:
            # fallback to positions if telemetry unavailable
            return await self.fetch("position", {"session_key": session_key})
        return data
