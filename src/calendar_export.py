from datetime import datetime, timedelta
from ics import Calendar, Event

def export_itinerary_to_ics(itinerary: dict, trip_info: dict) -> str:
    """Export itinerary to iCalendar format"""
    cal = Calendar()
    
    for day in itinerary.get('itinerary', []):
        date_str = day['date']
        schedule = day['schedule']
        
        # Parse schedule and create events
        # Simplified - in production, parse the actual schedule
        evt = Event()
        evt.name = f"Day {day['day']} - {trip_info['destination']}"
        evt.begin = datetime.fromisoformat(date_str)
        evt.description = schedule
        evt.duration = timedelta(hours=12)
        
        # Add reminder 1 day before
        evt.add_alarm(timedelta(hours=-24))
        
        cal.events.add(evt)
    
    # Save to file
    filename = f"trip_{trip_info['destination']}.ics"
    with open(filename, 'w') as f:
        f.writelines(cal)
    
    return filename
