"""Quick setup test"""
import sys
import os

def test_imports():
    """Test all required imports"""
    try:
        import openai
        print("✓ OpenAI installed")
    except ImportError:
        print("✗ OpenAI missing")
        
    try:
        import aiohttp
        print("✓ aiohttp installed")
    except ImportError:
        print("✗ aiohttp missing")
        
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv missing")
        
    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        print("✗ pandas missing")

def test_env():
    """Test environment configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv('OPENAI_API_KEY'):
        if os.getenv('OPENAI_API_KEY') != 'your_openai_key_here':
            print("✓ OpenAI API key configured")
        else:
            print("⚠ OpenAI API key not set (using placeholder)")
    else:
        print("✗ OpenAI API key missing")
        
    if os.getenv('WEATHERAPI_KEY'):
        print("✓ Weather API key configured")
    else:
        print("⚠ Weather API key not set (optional)")

def test_structure():
    """Test directory structure"""
    required_dirs = ['src', 'data', 'tests']
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"✓ {dir}/ exists")
        else:
            print(f"✗ {dir}/ missing")
            
    required_files = ['requirements.txt', '.env', '.gitignore']
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")

if __name__ == "__main__":
    print("\n=== Testing Imports ===")
    test_imports()
    
    print("\n=== Testing Environment ===")
    test_env()
    
    print("\n=== Testing Structure ===")
    test_structure()
    
    print("\n✅ Setup test complete!")
