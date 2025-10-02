import asyncio
import sys
sys.path.insert(0, 'src')
from travel_agent_roma import SentientTravelAgent

async def add_my_history():
    agent = SentientTravelAgent()
    history_agent = agent.meta_agent.history_agent
    
    # Add your past trips
    await history_agent._add_location({
        "name": "Paris",
        "country": "France",
        "visit_date": "2024-06-15",
        "duration_days": 5,
        "rating": 5,
        "notes": "Amazing food and culture"
    })
    
    await history_agent._add_location({
        "name": "Tokyo",
        "country": "Japan",
        "visit_date": "2024-09-20",
        "duration_days": 7,
        "rating": 5,
        "notes": "Incredible experience"
    })
    
    print("✅ Travel history added!")

asyncio.run(add_my_history())
