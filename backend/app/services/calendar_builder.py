from collections import defaultdict
from typing import Dict, List

def build_calendar(sessions: List[dict]) -> List[dict]:
    meetings: Dict[int, dict] = defaultdict(lambda: {
        "meeting_key": None,
        "meeting_name": "",
        "circuit": "",
        "country": "",
        "date_start": None,
        "sessions": []
    })

    for s in sessions:
        mk = s["meeting_key"]
        meetings[mk]["meeting_key"] = mk
        meetings[mk]["meeting_name"] = s.get("meeting_name")
        meetings[mk]["circuit"] = s.get("circuit_short_name")
        meetings[mk]["country"] = s.get("country_name")
        meetings[mk]["date_start"] = s.get("date_start")
        meetings[mk]["sessions"].append({
            "session_key": s["session_key"],
            "session_name": s["session_name"],
            "date_start": s["date_start"]
        })

    # Sort sessions inside each meeting
    for m in meetings.values():
        m["sessions"] = sorted(m["sessions"], key=lambda x: x["date_start"])

    # Sort meetings chronologically (season calendar order)
    calendar = sorted(meetings.values(), key=lambda x: x["date_start"])
    return calendar
