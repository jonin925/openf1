from app.services.calendar_service import CalendarService

service = CalendarService()

# First race weekend of 2025 (typically Bahrain GP)
sessions = service.get_sessions(year=2025)

print(f"Fetched {len(sessions)} sessions")
for s in sessions[:5]:
    print(s)
