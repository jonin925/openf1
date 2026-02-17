from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Session(BaseModel):
    session_key: int
    meeting_name: str
    session_name: str
    date_start: datetime

class Lap(BaseModel):
    driver_number: int
    lap_number: int
    lap_time: Optional[float]
    session_key: int
    date_start: Optional[datetime]

class Position(BaseModel):
    driver_number: int
    position: int
    session_key: int
    date: datetime

class TelemetryPoint(BaseModel):
    driver_number: int
    speed: Optional[float]
    x: Optional[float]
    y: Optional[float]
    date: datetime
