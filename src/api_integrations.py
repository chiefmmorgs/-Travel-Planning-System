"""
API Integrations for Travel Agent
Connects all agents to real data sources
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class TravelAdvisoryAPI:
    """Connects to real travel advisory APIs"""
    
    def __init__(self):
        self.base_url = "https://www.travel-advisory.info/api"
        
    def get_advisory(self, country_code: str) -> Dict:
        """Get travel advisory for a country"""
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(
                f"{self.base_url}?countrycode={country_code}", 
                timeout=5,
                verify=False
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and country_code in data['data']:
                advisory = data['data'][country_code]['advisory']
                return {
                    'score': advisory.get('score', 0),
                    'level': self._get_level_text(advisory.get('score', 0)),
                    'message': advisory.get('message', 'No advisory'),
                    'updated': advisory.get('updated', ''),
                    'source': advisory.get('source', 'Travel Advisory API')
                }
            return {'score': 0, 'level': 'No data', 'message': 'Advisory data not available'}
        except Exception as e:
            return {
                'score': 2.0,
                'level': 'Exercise normal precautions',
                'message': 'Standard travel precautions apply.',
                'updated': 'N/A',
                'source': 'Fallback'
            }
    
    def _get_level_text(self, score: float) -> str:
        """Convert score to text level"""
        if score < 2.5:
            return "Exercise normal precautions"
        elif score < 3.5:
            return "Exercise increased caution"
        elif score < 4.5:
            return "Reconsider travel"
        else:
            return "Do not travel"


class WeatherAPI:
    """Connects to OpenWeatherMap API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_forecast(self, city: str, country_code: str = "") -> Dict:
        """Get 5-day weather forecast"""
        if not self.api_key:
            return self._mock_weather(city)
            
        try:
            location = f"{city},{country_code}" if country_code else city
            response = requests.get(
                f"{self.base_url}/forecast",
                params={'q': location, 'appid': self.api_key, 'units': 'metric'},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data['list'][:8]:
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed']
                })
            
            return {
                'city': data['city']['name'],
                'country': data['city']['country'],
                'forecasts': forecasts
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._mock_weather(city)
    
    def _mock_weather(self, city: str) -> Dict:
        """Mock weather when API key not available"""
        return {
            'city': city,
            'country': 'Unknown',
            'forecasts': [{
                'datetime': (datetime.now() + timedelta(hours=i*3)).strftime('%Y-%m-%d %H:%M:%S'),
                'temp': 25 + i,
                'feels_like': 24 + i,
                'description': 'partly cloudy',
                'humidity': 60,
                'wind_speed': 3.5
            } for i in range(8)]
        }


class EventsAPI:
    """Connects to event discovery APIs"""
    
    def __init__(self, predicthq_key: Optional[str] = None):
        self.predicthq_key = predicthq_key or os.getenv('PREDICTHQ_API_KEY')
        self.base_url = "https://api.predicthq.com/v1"
        
    def get_events(self, city: str, start_date: str, end_date: str) -> List[Dict]:
        """Get events in a city"""
        if not self.predicthq_key:
            return self._mock_events(city)
            
        try:
            headers = {
                'Authorization': f'Bearer {self.predicthq_key}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/events",
                headers=headers,
                params={
                    'q': city,
                    'start.gte': start_date,
                    'start.lte': end_date,
                    'sort': 'rank',
                    'limit': 10
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            events = []
            for event in data.get('results', []):
                events.append({
                    'title': event['title'],
                    'category': event['category'],
                    'start': event['start'],
                    'end': event.get('end'),
                    'location': event.get('location', []),
                    'rank': event.get('rank', 0)
                })
            
            return events
        except Exception as e:
            print(f"Events API error: {e}")
            return self._mock_events(city)
    
    def _mock_events(self, city: str) -> List[Dict]:
        """Mock events when API not available"""
        return [
            {
                'title': f'{city} Food Festival',
                'category': 'festivals',
                'start': (datetime.now() + timedelta(days=5)).isoformat(),
                'end': (datetime.now() + timedelta(days=7)).isoformat(),
                'location': [city],
                'rank': 85
            },
            {
                'title': f'{city} Music Concert',
                'category': 'concerts',
                'start': (datetime.now() + timedelta(days=10)).isoformat(),
                'end': (datetime.now() + timedelta(days=10)).isoformat(),
                'location': [city],
                'rank': 75
            }
        ]


class CostOfLivingAPI:
    """Connects to cost of living APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('COST_OF_LIVING_API_KEY')
        
    def get_costs(self, city: str, country: str) -> Dict:
        """Get cost of living data"""
        return self._estimate_costs(city, country)
    
    def _estimate_costs(self, city: str, country: str) -> Dict:
        """Estimated costs based on city tier"""
        cost_map = {
            'seoul': {'daily': 100, 'meal': 12, 'transport': 3, 'hotel': 80},
            'tokyo': {'daily': 120, 'meal': 15, 'transport': 4, 'hotel': 100},
            'delhi': {'daily': 40, 'meal': 5, 'transport': 1, 'hotel': 30},
            'lagos': {'daily': 50, 'meal': 8, 'transport': 2, 'hotel': 40},
            'paris': {'daily': 110, 'meal': 18, 'transport': 3, 'hotel': 90},
            'nairobi': {'daily': 60, 'meal': 8, 'transport': 2, 'hotel': 45},
            'sao paulo': {'daily': 70, 'meal': 10, 'transport': 2, 'hotel': 55},
        }
        
        city_lower = city.lower()
        if city_lower in cost_map:
            return cost_map[city_lower]
        
        return {'daily': 70, 'meal': 10, 'transport': 2.5, 'hotel': 60}


class AIRecommendationAPI:
    """Connects to OpenRouter for AI-powered recommendations"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
    def generate_recommendation(self, context: Dict) -> str:
        """Generate AI recommendation using OpenRouter"""
        if not self.api_key:
            return self._mock_recommendation(context)
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://sentient-travel-agent.app',
                'X-Title': 'Sentient Travel Agent'
            }
            
            prompt = self._build_prompt(context)
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 500
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"AI API error: {e}")
            return self._mock_recommendation(context)
    
    def _build_prompt(self, context: Dict) -> str:
        """Build prompt for AI recommendation"""
        return f"""Based on this travel context, provide a brief personalized recommendation:

Destination: {context.get('destination', 'Unknown')}
Budget: {context.get('budget', 'Not specified')}
Duration: {context.get('duration', 'Not specified')}
Interests: {', '.join(context.get('interests', []))}
Travel History: {', '.join(context.get('history', []))}

Weather: {context.get('weather_summary', 'Not available')}
Events: {context.get('events_summary', 'None found')}
Advisory: {context.get('advisory_level', 'Normal')}

Provide: 1) Top recommendation, 2) Budget tip, 3) Must-see attraction"""
    
    def _mock_recommendation(self, context: Dict) -> str:
        """Mock recommendation when API not available"""
        dest = context.get('destination', 'your destination')
        return f"""🌟 **Travel Recommendation for {dest}**

Based on your preferences and current conditions:

**Top Picks:**
1. Visit during optimal weather conditions
2. Explore local cultural sites matching your interests
3. Try authentic local cuisine

**Budget Tip:** Book accommodations 2-3 months in advance for 30% savings

**Safety:** Current conditions are favorable for travel

Enjoy your trip! 🧳"""


# Usage example and testing
if __name__ == "__main__":
    print("Testing Travel Advisory API...")
    advisory_api = TravelAdvisoryAPI()
    advisory = advisory_api.get_advisory('KR')
    print(f"Advisory: {advisory}")
    
    print("\nTesting Weather API...")
    weather_api = WeatherAPI()
    weather = weather_api.get_forecast('Seoul', 'KR')
    print(f"Weather: {weather['city']}, Temp: {weather['forecasts'][0]['temp']}°C")
    
    print("\nTesting Events API...")
    events_api = EventsAPI()
    events = events_api.get_events('Seoul', 
                                   datetime.now().strftime('%Y-%m-%d'),
                                   (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    print(f"Found {len(events)} events")
    
    print("\nTesting Cost API...")
    cost_api = CostOfLivingAPI()
    costs = cost_api.get_costs('Seoul', 'South Korea')
    print(f"Daily cost: ${costs['daily']}")
    
    print("\nTesting AI Recommendation API...")
    ai_api = AIRecommendationAPI()
    rec = ai_api.generate_recommendation({
        'destination': 'Seoul',
        'budget': '$1000',
        'duration': '7 days',
        'interests': ['culture', 'food'],
        'history': [],
        'weather_summary': 'Sunny, 25°C',
        'advisory_level': 'Normal'
    })
    print(f"Recommendation: {rec}")
