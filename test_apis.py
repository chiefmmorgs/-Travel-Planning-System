from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load .env explicitly
load_dotenv('.env')

print("🔑 Checking API Keys...")
weather_key = os.getenv('OPENWEATHER_API_KEY')
predict_key = os.getenv('PREDICTHQ_API_KEY')
openrouter_key = os.getenv('OPENROUTER_API_KEY')

print(f"OpenWeather: {'✓ Set (' + weather_key[:10] + '...)' if weather_key else '✗ Missing'}")
print(f"PredictHQ: {'✓ Set' if predict_key else '✗ Missing'}")
print(f"OpenRouter: {'✓ Set (' + openrouter_key[:10] + '...)' if openrouter_key else '✗ Missing'}")
print()

# Test Weather API
from src.api_integrations import WeatherAPI
weather = WeatherAPI(weather_key)
result = weather.get_forecast('Seoul', 'KR')
print(f"🌤️  Weather Test:")
print(f"   City: {result['city']}")
print(f"   Temp: {result['forecasts'][0]['temp']}°C")
print(f"   Condition: {result['forecasts'][0]['description']}")
print(f"   Source: {'✅ REAL API' if result['country'] != 'Unknown' else '⚠️  Mock Data'}")
print()

# Test Events API
from src.api_integrations import EventsAPI
events_api = EventsAPI(predict_key)
events = events_api.get_events(
    'Seoul',
    datetime.now().strftime('%Y-%m-%d'),
    (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
)
print(f"🎉 Events Test:")
print(f"   Found {len(events)} events")
if events:
    print(f"   Next event: {events[0]['title']}")
print()

# Test AI API
from src.api_integrations import AIRecommendationAPI
ai = AIRecommendationAPI(openrouter_key)
rec = ai.generate_recommendation({
    'destination': 'Tokyo',
    'budget': '$1500',
    'interests': ['culture', 'food', 'technology']
})
print(f"🤖 AI Recommendation Test:")
print(f"   {rec[:150]}...")
print()

print("✅ All tests complete!")
