from fastapi import APIRouter
from services.openf1_client import OpenF1Client
from services.data_store import store

router = APIRouter()
client = OpenF1Client()

@router.get("/2025")
async def get_2025_sessions():
    if not store.sessions:
        sessions = await client.get_sessions_2025()
        store.sessions = sessions
    return store.sessions

@router.get("/{session_key}")
async def get_session_details(session_key: int):
    return {"session_key": session_key}
