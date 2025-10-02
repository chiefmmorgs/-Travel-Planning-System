"""Configuration management for Travel Agent"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""
    
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
    
    # Weather API (when you add it)
    WEATHERAPI_KEY = os.getenv('WEATHERAPI_KEY')
    
    # Agent settings
    AGENT_NAME = os.getenv('AGENT_NAME', 'TravelScout')
    WEEKLY_DIGEST_DAY = os.getenv('WEEKLY_DIGEST_DAY', 'monday')
    WEEKLY_DIGEST_TIME = os.getenv('WEEKLY_DIGEST_TIME', '09:00')
    
    # Data paths
    DATA_DIR = 'data'
    TRAVEL_HISTORY_FILE = f'{DATA_DIR}/travel_history.json'
    PREFERENCES_FILE = f'{DATA_DIR}/preferences.json'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in .env")
        return True

if __name__ == "__main__":
    Config.validate()
    print("✅ Configuration valid!")
