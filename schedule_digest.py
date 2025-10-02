import asyncio
import schedule
import time
import sys
sys.path.insert(0, 'src')
from travel_agent_roma import SentientTravelAgent

def run_digest():
    async def generate():
        agent = SentientTravelAgent()
        # Load trips from a file or database
        agent.add_trip("Paris", "2026-06-01", "2026-06-08", 3000)
        digest = await agent.generate_weekly_digest()
        
        # Save to file or send email
        with open('latest_digest.txt', 'w') as f:
            f.write(digest['digest']['recommendations'])
        
        print("✅ Weekly digest generated!")
    
    asyncio.run(generate())

# Schedule every Monday at 9 AM
schedule.every().monday.at("09:00").do(run_digest)

print("�� Scheduler running... (Ctrl+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(60)
