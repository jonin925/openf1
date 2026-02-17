from fastapi import APIRouter
from app.services.openf1_client import OpenF1Client
from app.services.calendar_builder import build_calendar
from app.services.data_store import store

router = APIRouter()
client = OpenF1Client()

@router.get("/2025")
async def season_calendar():
    if not store.sessions:
        store.sessions = await client.get_sessions_2025()

    return build_calendar(store.sessions)
