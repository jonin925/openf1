from fastapi import APIRouter
from services.openf1_client import OpenF1Client
from services.data_store import store

router = APIRouter()
client = OpenF1Client()

@router.get("/laps/{session_key}")
async def laps(session_key: int):
    if session_key not in store.laps:
        store.laps[session_key] = await client.get_laps(session_key)
    return store.laps[session_key]

@router.get("/positions/{session_key}")
async def positions(session_key: int):
    if session_key not in store.positions:
        store.positions[session_key] = await client.get_positions(session_key)
    return store.positions[session_key]

@router.get("/location/{session_key}")
async def telemetry(session_key: int):
    if session_key not in store.telemetry:
        store.telemetry[session_key] = await client.get_telemetry(session_key)
    return store.telemetry[session_key]
