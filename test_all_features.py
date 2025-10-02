"""Test all features of the Travel Agent"""
import asyncio
import sys
import json
sys.path.insert(0, 'src')

async def test_all():
    print("\n" + "="*60)
    print("TESTING ALL FEATURES")
    print("="*60)
    
    # 1. Test basic agent
    print("\n1. Testing basic ROMA agent...")
    from travel_agent_roma import SentientTravelAgent
    agent = SentientTravelAgent()
    agent.add_trip("Rome", "2026-04-01", "2026-04-08", 2800)
    print("   ✅ Agent created and trip added")
    
    # 2. Test config
    print("\n2. Testing configuration...")
    from src.config import Config
    Config.validate()
    print("   ✅ Configuration valid")
    
    # 3. Test utils
    print("\n3. Testing utilities...")
    from src.utils import format_date, save_digest
    formatted = format_date("2026-04-01")
    print(f"   ✅ Date formatting works: {formatted}")
    
    # 4. Test travel history
    print("\n4. Testing travel history...")
    with open('data/travel_history.json', 'r') as f:
        history = json.load(f)
    print(f"   ✅ History loaded: {len(history)} trips recorded")
    
    # 5. Test digest generation
    print("\n5. Testing digest generation...")
    digest = await agent.generate_weekly_digest()
    print("   ✅ Digest generated successfully")
    
    # 6. Save digest
    print("\n6. Testing digest save...")
    from src.utils import save_digest
    save_digest(digest, "test_digest.json")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! 🎉")
    print("="*60)

asyncio.run(test_all())
