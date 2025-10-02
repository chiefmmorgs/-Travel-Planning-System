"""Simple demo of the Travel Agent"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

# Simple test without full implementation
async def test_basic():
    print("🌍 Travel Agent Demo")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_key_here':
        print("⚠️  Warning: OpenAI API key not configured")
        print("   Set it in .env file for full functionality")
    else:
        print("✓ OpenAI API key configured")
    
    print("\n📍 Sample Trip:")
    print("  Destination: Bali, Indonesia")
    print("  Dates: Dec 1-10, 2025")
    print("  Budget: $3,000")
    
    print("\n✨ ROMA Architecture would:")
    print("  1. Decompose into parallel tasks")
    print("  2. Scan advisories, weather, events")
    print("  3. Analyze budget")
    print("  4. Generate AI recommendations")
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    asyncio.run(test_basic())
