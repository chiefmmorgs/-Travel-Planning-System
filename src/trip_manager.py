import json
import os
from datetime import datetime
from typing import List, Dict

class TripManager:
    """Manages trip data persistence"""
    
    def __init__(self):
        self.trips_file = "data/trips.json"
        self.user_profile_file = "data/user_profile.json"
        os.makedirs('data', exist_ok=True)
    
    def save_trip(self, trip: Dict) -> None:
        """Save a new trip"""
        trips = self.load_trips()
        trip['id'] = str(len(trips) + 1)
        trip['created_at'] = datetime.now().isoformat()
        trips.append(trip)
        
        with open(self.trips_file, 'w') as f:
            json.dump(trips, f, indent=2)
    
    def load_trips(self) -> List[Dict]:
        """Load all trips"""
        try:
            with open(self.trips_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def get_upcoming_trips(self) -> List[Dict]:
        """Get trips that haven't happened yet"""
        trips = self.load_trips()
        today = datetime.now().date()
        upcoming = [t for t in trips if datetime.fromisoformat(t['start_date']).date() >= today]
        return upcoming
    
    def save_user_profile(self, profile: Dict) -> None:
        """Save user profile with interests"""
        with open(self.user_profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def load_user_profile(self) -> Dict:
        """Load user profile"""
        try:
            with open(self.user_profile_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "home_country": "Nigeria",
                "home_city": "Port Harcourt",
                "interests": [],
                "profession": "",
                "passport_country": "Nigeria"
            }
