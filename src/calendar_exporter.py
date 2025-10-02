from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import pytz

class CalendarExporter:
    """Export itinerary to ICS calendar format"""
    
    def create_calendar(self, itinerary: Dict, user_timezone='Africa/Lagos'):
        """Create iCalendar file from itinerary"""
        cal = Calendar()
        cal.add('prodid', '-//Travel Scout//EN')
        cal.add('version', '2.0')
        
        # Parse itinerary and create events
        # This is a simplified version - real implementation would parse the AI-generated itinerary
        
        return cal.to_ical()
    
    def add_event(self, cal: Calendar, name: str, start: datetime, 
                  duration: int, location: str, description: str = ""):
        """Add event to calendar with reminder"""
        event = Event()
        event.add('summary', name)
        event.add('dtstart', start)
        event.add('dtend', start + timedelta(minutes=duration))
        event.add('location', location)
        event.add('description', description)
        
        # Add 30-minute reminder
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('trigger', timedelta(minutes=-30))
        alarm.add('description', f'Reminder: {name} in 30 minutes')
        event.add_component(alarm)
        
        cal.add_component(event)
