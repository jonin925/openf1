import asyncio
from app.services.openf1_client import OpenF1Client
from app.services.data_store import store

client = OpenF1Client()

async def preload_2025():
    sessions = await client.get_sessions_2025()
    store.sessions = sessions

    # Filter only race sessions (more reliable telemetry availability)
    race_sessions = [s for s in sessions if s.get("session_name", "").lower() == "race"]

    if not race_sessions:
        print("No race sessions found for 2025")
        return

    first_race_key = race_sessions[0]["session_key"]
    print(f"Using race session_key={first_race_key}")

    store.laps[first_race_key] = await client.get_laps(first_race_key)
    store.positions[first_race_key] = await client.get_positions(first_race_key)
    store.telemetry[first_race_key] = await client.get_telemetry(first_race_key)

    print("Preload complete")

if __name__ == "__main__":
    asyncio.run(preload_2025())
