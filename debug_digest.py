import asyncio
import sys
import json
sys.path.insert(0, 'src')
from travel_agent_roma import SentientTravelAgent

async def debug():
    agent = SentientTravelAgent()
    agent.add_trip("Kenya", "2025-10-01", "2025-10-10", 2000)
    
    digest = await agent.generate_weekly_digest()
    
    print("\n" + "="*60)
    print("FULL DIGEST STRUCTURE:")
    print("="*60)
    print(json.dumps(digest, indent=2))
    
    print("\n" + "="*60)
    print("INTELLIGENCE DATA:")
    print("="*60)
    for intel in digest['context'].get('intelligence', []):
        print(json.dumps(intel, indent=2))

asyncio.run(debug())
