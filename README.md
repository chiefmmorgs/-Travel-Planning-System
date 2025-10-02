# AI Travel Planning System

Complete travel planning system with real-time data integration and intelligent agent orchestration.

## Features

- Real-time currency conversion (161 currencies)
  
- Live weather forecasts per destination

- Actual events (concerts, festivals, exhibitions)
  
- AI-powered personalized recommendations
  
- Flight search with entry city optimization
  
- Wikipedia city guides
  
- Per-trip intelligence reports

## Quick Start

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```
2. Setup API Keys (Optional)
The system works without API keys using mock data. Add keys for real-time data:
```
bashcp .env.example .env
nano .env
```
Add your keys:
```
OPENWEATHER_API_KEY=your_key_here
PREDICTHQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```
Get free API keys:

OpenWeatherMap: https://openweathermap.org/api (1000 calls/day free)

PredictHQ: https://www.predicthq.com/ (1000 requests/month free)

OpenRouter: https://openrouter.ai/ (pay-as-you-go, ~$0.003 per request)

3. Run the App
```
streamlit run streamlit_app.py
```
Open http://localhost:8501 in your browser.


Project Structure
```
.
├── streamlit_app.py          # Main application
├── src/
│   ├── agents.py             # 8 intelligent agents
│   ├── api_integrations.py   # API wrappers
│   ├── flight_search.py      # Flight search system
│   ├── localization.py       # Currency conversion
│   └── trip_manager.py       # Data management
├── data/                     # Trip & profile storage
└── requirements.txt          # Dependencies
```
**Architecture**

ROMA (Recursive Orchestration Meta-Agent) system with 8 agents:

TravelDigestMetaAgent (orchestrator)

TripIntelligenceAgent (coordinator)

WeatherScannerAgent

AdvisoryScannerAgent

EventDiscoveryAgent

BudgetAnalysisAgent

RecommendationGeneratorAgent

DestinationDiscoveryAgent


**API Integrations**
```
OpenWeatherMap: Real weather forecasts

PredictHQ: Live event discovery

OpenRouter: Claude-powered recommendations

ExchangeRate-API: Real-time currency rates

Travel Advisory API: Government safety advisories

Wikipedia: City guides and attractions
```

**Without API Keys**
```
The system works fully in mock mode with realistic sample data. Add API keys to unlock:

Actual weather (not generic 25°C)

Real events happening now

Unique AI recommendations per destination

Live exchange rates
```
**Troubleshooting**
```
"API integrations not available"

**Normal without API keys**
System uses intelligent mock data

keys to .env for real data

"Exchange rates updated: Fallback rates"
```
**Using estimated rates**
```
Internet connection required for live rates
```
**Import errors**
```
Ensure you're in venv: source venv/bin/activate

Install dependencies: pip install -r requirements.txt
```
License
MIT
