from fastapi import FastAPI
from routers import sessions, telemetry
from routers import calendar

app = FastAPI(title="F1 Open Data Dashboard")

app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])

@app.get("/health")
async def health():
    return {"status": "ok"}
