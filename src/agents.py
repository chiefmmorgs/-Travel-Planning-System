"""
ROMA Architecture - All Agents Connected to Real APIs
"""

from datetime import datetime, timedelta
from typing import Dict, List
import os

try:
    from src.api_integrations import (
        TravelAdvisoryAPI, WeatherAPI, EventsAPI,
        CostOfLivingAPI, AIRecommendationAPI
    )
    APIS_AVAILABLE = True
except ImportError:
    APIS_AVAILABLE = False
    print("Warning: API integrations not available. Using mock data.")


class BaseAgent:
    """Base class for all agents"""
    def __init__(self, name: str):
        self.name = name
        
    def log(self, message: str):
        print(f"[{self.name}] {message}")


class AdvisoryScannerAgent(BaseAgent):
    """Scans travel advisories using real APIs"""
    
    def __init__(self):
        super().__init__("AdvisoryScannerAgent")
        if APIS_AVAILABLE:
            self.api = TravelAdvisoryAPI()
        
        self.country_codes = {
            'south korea': 'KR', 'korea': 'KR', 'seoul': 'KR',
            'india': 'IN', 'delhi': 'IN', 'mumbai': 'IN',
            'japan': 'JP', 'tokyo': 'JP',
            'nigeria': 'NG', 'lagos': 'NG',
            'france': 'FR', 'paris': 'FR',
            'egypt': 'EG', 'cairo': 'EG',
            'singapore': 'SG',
            'usa': 'US', 'united states': 'US',
            'uk': 'GB', 'united kingdom': 'GB',
            'germany': 'DE', 'brazil': 'BR',
            'kenya': 'KE', 'nairobi': 'KE',
        }
    
    def execute(self, destination: str) -> Dict:
        """Fetch real travel advisories"""
        self.log("Executing directly")
        
        dest_lower = destination.lower()
        country_code = self.country_codes.get(dest_lower, 'US')
        
        if APIS_AVAILABLE:
            advisory = self.api.get_advisory(country_code)
            return {
                'destination': destination,
                'safety_level': advisory['level'],
                'safety_score': advisory['score'],
                'advisory_message': advisory['message'],
                'last_updated': advisory.get('updated', 'Unknown'),
                'source': advisory.get('source', 'Travel Advisory API')
            }
        
        return {
            'destination': destination,
            'safety_level': 'Exercise normal precautions',
            'safety_score': 2.0,
            'advisory_message': 'No significant security concerns',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Mock Data'
        }


class WeatherScannerAgent(BaseAgent):
    """Scans weather using OpenWeatherMap API"""
    
    def __init__(self):
        super().__init__("WeatherScannerAgent")
        if APIS_AVAILABLE:
            self.api = WeatherAPI(os.getenv('OPENWEATHER_API_KEY'))
        
        self.city_map = {
            'south korea': 'Seoul', 'korea': 'Seoul',
            'india': 'Delhi',
            'japan': 'Tokyo',
            'nigeria': 'Lagos',
            'france': 'Paris',
            'kenya': 'Nairobi',
            'brazil': 'Sao Paulo',
            'egypt': 'Cairo',
            'singapore': 'Singapore'
        }
    
    def execute(self, destination: str) -> Dict:
        """Fetch real weather forecast"""
        self.log("Executing directly")
        
        dest_lower = destination.lower()
        city = self.city_map.get(dest_lower, destination)
        
        if APIS_AVAILABLE and self.api:
            forecast = self.api.get_forecast(city)
            
            temps = [f['temp'] for f in forecast['forecasts']]
            avg_temp = sum(temps) / len(temps) if temps else 25
            
            conditions = [f['description'] for f in forecast['forecasts']]
            main_condition = max(set(conditions), key=conditions.count)
            
            return {
                'destination': destination,
                'city': forecast['city'],
                'avg_temp': round(avg_temp, 1),
                'condition': main_condition,
                'humidity': forecast['forecasts'][0]['humidity'],
                'forecast_days': len(forecast['forecasts']) // 3,
                'detailed_forecast': forecast['forecasts'][:5]
            }
        
        return {
            'destination': destination,
            'city': city,
            'avg_temp': 25.0,
            'condition': 'partly cloudy',
            'humidity': 60,
            'forecast_days': 3,
            'detailed_forecast': []
        }


class EventDiscoveryAgent(BaseAgent):
    """Discovers local events using real APIs"""
    
    def __init__(self):
        super().__init__("EventDiscoveryAgent")
        if APIS_AVAILABLE:
            self.api = EventsAPI(os.getenv('PREDICTHQ_API_KEY'))
        
        self.city_map = {
            'south korea': 'Seoul', 'korea': 'Seoul',
            'india': 'Delhi',
            'japan': 'Tokyo',
            'nigeria': 'Lagos',
            'france': 'Paris',
            'kenya': 'Nairobi',
            'brazil': 'Sao Paulo',
            'egypt': 'Cairo',
            'singapore': 'Singapore'
        }
    
    def execute(self, destination: str, start_date: str = None, end_date: str = None) -> Dict:
        """Fetch real events"""
        self.log("Executing directly")
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        dest_lower = destination.lower()
        city = self.city_map.get(dest_lower, destination)
        
        if APIS_AVAILABLE and self.api:
            events = self.api.get_events(city, start_date, end_date)
            
            return {
                'destination': destination,
                'city': city,
                'event_count': len(events),
                'events': events,
                'date_range': f"{start_date} to {end_date}"
            }
        
        return {
            'destination': destination,
            'city': city,
            'event_count': 2,
            'events': [
                {
                    'title': f'{city} Cultural Festival',
                    'category': 'festivals',
                    'start': (datetime.now() + timedelta(days=7)).isoformat(),
                    'rank': 80
                },
                {
                    'title': f'{city} Night Market',
                    'category': 'community',
                    'start': (datetime.now() + timedelta(days=3)).isoformat(),
                    'rank': 70
                }
            ],
            'date_range': f"{start_date} to {end_date}"
        }


class BudgetAnalysisAgent(BaseAgent):
    """Analyzes budget using cost of living data"""
    
    def __init__(self):
        super().__init__("BudgetAnalysisAgent")
        if APIS_AVAILABLE:
            self.api = CostOfLivingAPI()
        
        self.city_country_map = {
            'south korea': ('Seoul', 'South Korea'),
            'korea': ('Seoul', 'South Korea'),
            'india': ('Delhi', 'India'),
            'japan': ('Tokyo', 'Japan'),
            'nigeria': ('Lagos', 'Nigeria'),
            'france': ('Paris', 'France'),
            'kenya': ('Nairobi', 'Kenya'),
            'brazil': ('Sao Paulo', 'Brazil'),
            'egypt': ('Cairo', 'Egypt'),
            'singapore': ('Singapore', 'Singapore')
        }
    
    def execute(self, destination: str, budget: float, duration_days: int) -> Dict:
        """Analyze budget feasibility"""
        self.log("Executing directly")
        
        dest_lower = destination.lower()
        city, country = self.city_country_map.get(dest_lower, (destination, 'Unknown'))
        
        if APIS_AVAILABLE and self.api:
            costs = self.api.get_costs(city, country)
        else:
            costs = {'daily': 70, 'meal': 10, 'transport': 2.5, 'hotel': 60}
        
        daily_cost = costs['daily']
        total_estimated = daily_cost * duration_days
        remaining = budget - total_estimated
        feasibility_pct = (budget / total_estimated * 100) if total_estimated > 0 else 100
        
        return {
            'destination': destination,
            'budget': budget,
            'duration_days': duration_days,
            'daily_cost': daily_cost,
            'total_estimated': total_estimated,
            'remaining_budget': remaining,
            'feasibility_percentage': min(feasibility_pct, 100),
            'is_feasible': remaining >= 0,
            'breakdown': costs
        }


class RecommendationGeneratorAgent(BaseAgent):
    """Generates AI-powered recommendations"""
    
    def __init__(self):
        super().__init__("RecommendationGeneratorAgent")
        if APIS_AVAILABLE:
            self.api = AIRecommendationAPI(os.getenv('OPENROUTER_API_KEY'))
    
    def execute(self, context: Dict) -> Dict:
        """Generate personalized recommendation"""
        self.log("Executing directly")
        
        if APIS_AVAILABLE and self.api:
            recommendation = self.api.generate_recommendation(context)
        else:
            dest = context.get('destination', 'your destination')
            recommendation = f"""🌟 **Travel Recommendation for {dest}**

Based on your preferences and current conditions:

**Top Picks:**
1. Visit during optimal weather conditions
2. Explore local cultural sites matching your interests
3. Try authentic local cuisine

**Budget Tip:** Book accommodations 2-3 months in advance

**Safety:** Current conditions are favorable for travel

Enjoy your trip! 🧳"""
        
        return {
            'recommendation': recommendation,
            'generated_at': datetime.now().isoformat(),
            'context_used': list(context.keys())
        }


class TravelHistoryAgent(BaseAgent):
    """Analyzes travel history patterns"""
    
    def __init__(self):
        super().__init__("TravelHistoryAgent")
    
    def execute(self, trips: List[Dict]) -> Dict:
        """Analyze travel patterns"""
        self.log("Executing directly")
        
        if not trips:
            return {
                'total_trips': 0,
                'destinations_visited': [],
                'total_spent': 0,
                'avg_trip_duration': 0,
                'patterns': 'No travel history yet'
            }
        
        destinations = [t.get('destination', 'Unknown') for t in trips]
        total_spent = sum(float(t.get('budget', 0)) for t in trips)
        
        return {
            'total_trips': len(trips),
            'destinations_visited': list(set(destinations)),
            'total_spent': total_spent,
            'avg_trip_duration': 7,
            'favorite_destination': max(set(destinations), key=destinations.count) if destinations else None,
            'patterns': f"Visited {len(set(destinations))} unique destinations"
        }


class DestinationDiscoveryAgent(BaseAgent):
    """Discovers new destinations based on preferences"""
    
    def __init__(self):
        super().__init__("DestinationDiscoveryAgent")
    
    def execute(self, interests: List[str], history: List[str], budget_range: str = "medium") -> Dict:
        """Suggest new destinations"""
        self.log("Executing directly")
        
        recommendations = {
            'culture': ['Kyoto', 'Istanbul', 'Rome', 'Cairo'],
            'adventure': ['Patagonia', 'Nepal', 'Iceland', 'New Zealand'],
            'food': ['Tokyo', 'Bangkok', 'Lima', 'Barcelona'],
            'nature': ['Costa Rica', 'Norway', 'Tanzania', 'Canada'],
            'history': ['Athens', 'Jerusalem', 'Petra', 'Angkor Wat'],
            'nightlife': ['Berlin', 'Ibiza', 'Las Vegas', 'Amsterdam'],
            'shopping': ['Dubai', 'Singapore', 'Milan', 'Hong Kong'],
            'relaxation': ['Maldives', 'Bali', 'Santorini', 'Seychelles']
        }
        
        suggested = []
        for interest in interests:
            if interest.lower() in recommendations:
                suggested.extend(recommendations[interest.lower()])
        
        suggested = [d for d in suggested if d not in history]
        suggested = list(dict.fromkeys(suggested))[:5]
        
        return {
            'based_on_interests': interests,
            'avoiding_history': history,
            'budget_range': budget_range,
            'suggested_destinations': suggested,
            'suggestion_count': len(suggested)
        }


class TripIntelligenceAgent(BaseAgent):
    """Meta-agent that coordinates trip intelligence gathering"""
    
    def __init__(self):
        super().__init__("TripIntelligenceAgent")
        self.budget_agent = BudgetAnalysisAgent()
        self.advisory_agent = AdvisoryScannerAgent()
        self.weather_agent = WeatherScannerAgent()
        self.events_agent = EventDiscoveryAgent()
    
    def execute(self, destination: str, budget: float = 1000, duration: int = 7) -> Dict:
        """Gather all intelligence for a trip"""
        self.log(f"Gathering intelligence for: {destination}")
        self.log("Decomposing into 4 subtasks")
        
        budget_analysis = self.budget_agent.execute(destination, budget, duration)
        advisory = self.advisory_agent.execute(destination)
        weather = self.weather_agent.execute(destination)
        events = self.events_agent.execute(destination)
        
        return {
            'destination': destination,
            'budget_analysis': budget_analysis,
            'safety_advisory': advisory,
            'weather_forecast': weather,
            'local_events': events,
            'intelligence_gathered_at': datetime.now().isoformat()
        }


class TravelDigestMetaAgent(BaseAgent):
    """Top-level meta-agent that orchestrates the weekly digest"""
    
    def __init__(self):
        super().__init__("TravelDigestMetaAgent")
        self.history_agent = TravelHistoryAgent()
        self.trip_intel_agent = TripIntelligenceAgent()
        self.discovery_agent = DestinationDiscoveryAgent()
        self.recommendation_agent = RecommendationGeneratorAgent()
    
    def execute(self, trips: List[Dict], user_profile: Dict) -> Dict:
        """Generate complete weekly digest"""
        self.log("Decomposing into 4 subtasks")
        
        history_analysis = self.history_agent.execute(trips)
        
        trip_intelligence = []
        for trip in trips:
            intel = self.trip_intel_agent.execute(
                trip.get('destination', 'Unknown'),
                float(trip.get('budget', 1000)),
                7
            )
            trip_intelligence.append(intel)
        
        interests = user_profile.get('interests', ['Culture', 'Adventure'])
        visited = history_analysis.get('destinations_visited', [])
        new_destinations = self.discovery_agent.execute(interests, visited)
        
        # Build context for AI recommendation
        recommendation_context = {
            'destination': trips[0].get('destination') if trips else 'Unknown',
            'budget': trips[0].get('budget') if trips else '1000',
            'interests': interests,
            'history': visited,
            'weather_summary': trip_intelligence[0]['weather_forecast']['condition'] if trip_intelligence else 'Unknown',
            'events_summary': f"{trip_intelligence[0]['local_events']['event_count']} events found" if trip_intelligence else 'None',
            'advisory_level': trip_intelligence[0]['safety_advisory']['safety_level'] if trip_intelligence else 'Normal'
        }
        recommendation = self.recommendation_agent.execute(recommendation_context)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'travel_history': history_analysis,
            'upcoming_trips_intelligence': trip_intelligence,
            'new_destinations': new_destinations,
            'ai_recommendation': recommendation,
            'digest_version': '2.0-real-apis'
        }
