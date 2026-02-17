from typing import Dict, List

class DataStore:
    def __init__(self):
        self.sessions: List[dict] = []
        self.laps: Dict[int, List[dict]] = {}
        self.positions: Dict[int, List[dict]] = {}
        self.telemetry: Dict[int, List[dict]] = {}

store = DataStore()
