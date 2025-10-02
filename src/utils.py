"""Utility functions for Travel Agent"""
import json
from datetime import datetime
from typing import Dict, Any

def format_date(date_str: str) -> str:
    """Format date string nicely"""
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime("%B %d, %Y")
    except:
        return date_str

def save_digest(digest: Dict[str, Any], filename: str = None):
    """Save digest to file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"digest_{timestamp}.json"
    
    with open(f"data/{filename}", 'w') as f:
        json.dump(digest, f, indent=2)
    
    print(f"✅ Digest saved to data/{filename}")

def load_trips_from_file(filename: str = "data/trips.json"):
    """Load trips from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_trips_to_file(trips: list, filename: str = "data/trips.json"):
    """Save trips to JSON file"""
    with open(filename, 'w') as f:
        json.dump(trips, f, indent=2)
