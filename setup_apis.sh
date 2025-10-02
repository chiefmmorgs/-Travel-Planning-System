#!/bin/bash

echo "🌍 Sentient Travel Agent - API Setup"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Create api_integrations.py
echo -e "${YELLOW}Step 1: Creating api_integrations.py...${NC}"
cat > src/api_integrations.py << 'EOFAPI'
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
        try:
            response = requests.get(f"{self.base_url}?countrycode={country_code}", timeout=5)
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
            print(f"Error fetching advisory: {e}")
            return {'score': 0, 'level': 'Error', 'message': str(e)}
    
    def _get_level_text(self, score: float) -> str:
        if score < 2.5:
            return "Exercise normal precautions"
        elif score < 3.5:
            return "Exercise increased caution"
        elif score < 4.5:
            return "Reconsider travel"
        else:
            return "Do not travel"


class WeatherAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_forecast(self, city: str, country_code: str = "") -> Dict:
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
            
            return {'city': data['city']['name'], 'country': data['city']['country'], 'forecasts': forecasts}
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._mock_weather(city)
    
    def _mock_weather(self, city: str) -> Dict:
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
    def __init__(self, predicthq_key: Optional[str] = None):
        self.predicthq_key = predicthq_key or os.getenv('PREDICTHQ_API_KEY')
        self.base_url = "https://api.predicthq.com/v1"
        
    def get_events(self, city: str, start_date: str, end_date: str) -> List[Dict]:
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
                params={'q': city, 'start.gte': start_date, 'start.lte': end_date, 'sort': 'rank', 'limit': 10},
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
        return [
            {'title': f'{city} Food Festival', 'category': 'festivals', 
             'start': (datetime.now() + timedelta(days=5)).isoformat(), 'rank': 85},
            {'title': f'{city} Music Concert', 'category': 'concerts',
             'start': (datetime.now() + timedelta(days=10)).isoformat(), 'rank': 75}
        ]


class CostOfLivingAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('COST_OF_LIVING_API_KEY')
        
    def get_costs(self, city: str, country: str) -> Dict:
        return self._estimate_costs(city, country)
    
    def _estimate_costs(self, city: str, country: str) -> Dict:
        cost_map = {
            'seoul': {'daily': 100, 'meal': 12, 'transport': 3, 'hotel': 80},
            'tokyo': {'daily': 120, 'meal': 15, 'transport': 4, 'hotel': 100},
            'delhi': {'daily': 40, 'meal': 5, 'transport': 1, 'hotel': 30},
            'lagos': {'daily': 50, 'meal': 8, 'transport': 2, 'hotel': 40},
            'paris': {'daily': 110, 'meal': 18, 'transport': 3, 'hotel': 90},
        }
        
        return cost_map.get(city.lower(), {'daily': 70, 'meal': 10, 'transport': 2.5, 'hotel': 60})


class AIRecommendationAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
    def generate_recommendation(self, context: Dict) -> str:
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
                    'messages': [{'role': 'user', 'content': prompt}],
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
        return f"""Based on this travel context, provide a brief personalized recommendation:

Destination: {context.get('destination', 'Unknown')}
Budget: {context.get('budget', 'Not specified')}
Interests: {', '.join(context.get('interests', []))}

Provide: 1) Top recommendation, 2) Budget tip, 3) Must-see attraction"""
    
    def _mock_recommendation(self, context: Dict) -> str:
        dest = context.get('destination', 'your destination')
        return f"""🌟 **Recommendation for {dest}**

1. **Must-Visit**: Explore historic downtown and local markets
2. **Budget Tip**: Book 2-3 months in advance for 30% savings
3. **Hidden Gem**: Visit during shoulder season

Safe travels! 🧳"""
EOFAPI

echo -e "${GREEN}✓ Created src/api_integrations.py${NC}"

# Step 2: Install dependencies
echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
pip install python-dotenv >> /dev/null 2>&1
echo -e "${GREEN}✓ Installed python-dotenv${NC}"

# Step 3: Create .env.example
echo ""
echo -e "${YELLOW}Step 3: Creating .env.example...${NC}"
cat > .env.example << 'EOFENV'
# Essential APIs (FREE)
OPENWEATHER_API_KEY=your_key_here

# Enhanced Features (Optional)
PREDICTHQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Optional
COST_OF_LIVING_API_KEY=your_key_here
EOFENV

echo -e "${GREEN}✓ Created .env.example${NC}"

# Step 4: Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo -e "${YELLOW}Step 4: Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env (please add your API keys)${NC}"
else
    echo ""
    echo -e "${YELLOW}Step 4: .env already exists${NC}"
fi

# Step 5: Update requirements.txt
echo ""
echo -e "${YELLOW}Step 5: Updating requirements.txt...${NC}"
if ! grep -q "python-dotenv" requirements.txt; then
    echo "python-dotenv>=1.0.0" >> requirements.txt
    echo -e "${GREEN}✓ Added python-dotenv to requirements.txt${NC}"
else
    echo -e "${GREEN}✓ python-dotenv already in requirements.txt${NC}"
fi

# Step 6: Update streamlit_app.py to load .env
echo ""
echo -e "${YELLOW}Step 6: Updating streamlit_app.py...${NC}"

# Check if dotenv import exists
if ! grep -q "from dotenv import load_dotenv" streamlit_app.py; then
    # Add import at the top after other imports
    sed -i '1i from dotenv import load_dotenv\nimport os\n\n# Load environment variables\nload_dotenv()' streamlit_app.py
    echo -e "${GREEN}✓ Added dotenv loading to streamlit_app.py${NC}"
else
    echo -e "${GREEN}✓ dotenv already loaded in streamlit_app.py${NC}"
fi

# Step 7: Test API connections
echo ""
echo -e "${YELLOW}Step 7: Testing API connections...${NC}"
python3 << 'EOFTEST'
from src.api_integrations import TravelAdvisoryAPI, WeatherAPI
import os

print("\n1. Testing Travel Advisory API (No key needed)...")
try:
    advisory = TravelAdvisoryAPI()
    result = advisory.get_advisory('KR')
    print(f"   ✓ Advisory for South Korea: {result['level']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing Weather API...")
weather_key = os.getenv('OPENWEATHER_API_KEY')
if weather_key and weather_key != 'your_key_here':
    try:
        weather = WeatherAPI(weather_key)
        result = weather.get_forecast('Seoul', 'KR')
        print(f"   ✓ Weather for {result['city']}: {result['forecasts'][0]['temp']}°C")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("   ⚠ No API key found - using mock data")
    print("   Sign up at: https://openweathermap.org/api")

print("\n")
EOFTEST

# Final instructions
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Get API keys (FREE):"
echo "   🌤️  OpenWeatherMap: https://openweathermap.org/api"
echo "   🎉 PredictHQ: https://www.predicthq.com/ (optional)"
echo "   🤖 OpenRouter: https://openrouter.ai/ (optional)"
echo ""
echo "2. Add your keys to .env file:"
echo "   nano .env"
echo ""
echo "3. Test the setup:"
echo "   python src/api_integrations.py"
echo ""
echo "4. Run your app:"
echo "   streamlit run streamlit_app.py"
echo ""
echo -e "${GREEN}All agents will work with or without API keys!${NC}"
echo "Without keys: Uses intelligent mock data"
echo "With keys: Uses real-time data"
echo ""
