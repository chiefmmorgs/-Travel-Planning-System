#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, 'src')
from travel_agent_roma import SentientTravelAgent

async def main():
    agent = SentientTravelAgent()
    
    print("🌍 Travel Agent CLI")
    print("=" * 50)
    
    # Interactive trip input
    destination = input("Destination: ")
    start_date = input("Start date (YYYY-MM-DD): ")
    end_date = input("End date (YYYY-MM-DD): ")
    budget = float(input("Budget ($): "))
    
    agent.add_trip(destination, start_date, end_date, budget)
    
    print("\n⏳ Generating digest...")
    digest = await agent.generate_weekly_digest()
    
    # Pretty print recommendations
    print("\n" + "=" * 50)
    print(digest['digest']['recommendations'])
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
