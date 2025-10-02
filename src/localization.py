"""
Localization module with REAL-TIME exchange rates
Using ExchangeRate-API.com (FREE - supports 161 currencies including NGN)
"""

import requests
from datetime import datetime
from typing import Dict, Optional

class Localizer:
    """Handles localization for currency, units, and time"""
    
    def __init__(self, currency: str = 'USD', units: str = 'metric', time_format: str = '24h'):
        self.user_currency = currency
        self.units = units
        self.time_format = time_format
        self.exchange_rates = {}
        self.last_updated = None
        
        # Fetch real rates on initialization
        self.fetch_exchange_rates()
    
    def fetch_exchange_rates(self) -> Dict[str, float]:
        """
        Fetch REAL-TIME exchange rates from ExchangeRate-API.com
        FREE - No API key needed for basic usage
        Supports 161 currencies including NGN, INR, KRW, KES, etc.
        """
        try:
            # ExchangeRate-API.com - FREE, supports all currencies
            response = requests.get(
                'https://open.er-api.com/v6/latest/USD',
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if data['result'] == 'success':
                self.exchange_rates = data['rates']
                self.last_updated = data['time_last_update_utc']
                
                print(f"✓ Live exchange rates updated: {self.last_updated}")
                print(f"  Sample: 1 USD = {self.exchange_rates.get('NGN', 'N/A')} NGN")
                print(f"  Sample: 1 USD = {self.exchange_rates.get('EUR', 'N/A')} EUR")
                return self.exchange_rates
            else:
                raise Exception("API returned error")
                
        except Exception as e:
            print(f"Warning: Could not fetch live rates: {e}")
            print("Using fallback rates (may be outdated)")
            
            # Fallback rates (approximate as of Oct 2024)
            self.exchange_rates = {
                'USD': 1.0,
                'EUR': 0.85,
                'GBP': 0.74,
                'NGN': 1580.0,  # Nigerian Naira
                'JPY': 149.0,
                'INR': 83.0,
                'KRW': 1330.0,
                'BRL': 4.95,
                'KES': 129.0,
                'GHS': 15.8,  # Ghana Cedi
                'ZAR': 18.5,  # South African Rand
                'EGP': 49.0,  # Egyptian Pound
            }
            self.last_updated = 'Fallback rates'
            return self.exchange_rates
    
    def convert_currency(self, amount_usd: float, target_currency: Optional[str] = None) -> Dict:
        """Convert USD to target currency using REAL-TIME rates"""
        target = target_currency or self.user_currency
        
        # Ensure we have rates
        if not self.exchange_rates:
            self.fetch_exchange_rates()
        
        # Get rate
        rate = self.exchange_rates.get(target, 1.0)
        converted_amount = amount_usd * rate
        
        # Currency symbols
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'NGN': '₦',
            'JPY': '¥', 'INR': '₹', 'KRW': '₩', 'BRL': 'R$',
            'KES': 'KSh', 'GHS': 'GH₵', 'ZAR': 'R', 'EGP': 'E£'
        }
        
        symbol = currency_symbols.get(target, target + ' ')
        
        return {
            'original': f'${amount_usd:,.2f}',
            'converted': f'{symbol}{converted_amount:,.2f}',
            'rate': rate,
            'target_currency': target,
            'last_updated': self.last_updated
        }
    
    def get_rate(self, currency: str) -> float:
        """Get exchange rate for a specific currency"""
        if not self.exchange_rates:
            self.fetch_exchange_rates()
        return self.exchange_rates.get(currency, 1.0)
    
    def convert_distance(self, km: float) -> str:
        """Convert kilometers to user's preferred units"""
        if self.units == 'imperial':
            miles = km * 0.621371
            return f"{miles:.1f} mi"
        return f"{km:.1f} km"
    
    def convert_temp(self, celsius: float) -> str:
        """Convert Celsius to user's preferred units"""
        if self.units == 'imperial':
            fahrenheit = (celsius * 9/5) + 32
            return f"{fahrenheit:.1f}°F"
        return f"{celsius:.1f}°C"
    
    def format_time(self, hour: int, minute: int) -> str:
        """Format time in user's preferred format"""
        if self.time_format == '12h':
            period = 'AM' if hour < 12 else 'PM'
            display_hour = hour % 12
            if display_hour == 0:
                display_hour = 12
            return f"{display_hour}:{minute:02d} {period}"
        return f"{hour:02d}:{minute:02d}"
    
    def format_date(self, date_str: str) -> str:
        """Format date according to locale"""
        return date_str


if __name__ == "__main__":
    print("Testing REAL-TIME Exchange Rates...\n")
    
    # Test NGN
    loc_ngn = Localizer('NGN', 'metric', '24h')
    result = loc_ngn.convert_currency(100)
    print(f"\n💵 NGN (Nigerian Naira):")
    print(f"  {result['original']} = {result['converted']}")
    print(f"  Rate: 1 USD = {result['rate']:.2f} NGN")
    print(f"  Updated: {result['last_updated']}")
    
    # Test EUR
    loc_eur = Localizer('EUR', 'metric', '24h')
    result = loc_eur.convert_currency(100)
    print(f"\n💶 EUR (Euro):")
    print(f"  {result['original']} = {result['converted']}")
    print(f"  Rate: 1 USD = {result['rate']:.4f} EUR")
    
    # Test GBP
    loc_gbp = Localizer('GBP', 'metric', '24h')
    result = loc_gbp.convert_currency(100)
    print(f"\n💷 GBP (British Pound):")
    print(f"  {result['original']} = {result['converted']}")
    print(f"  Rate: 1 USD = {result['rate']:.4f} GBP")
    
    # Test INR
    loc_inr = Localizer('INR', 'metric', '24h')
    result = loc_inr.convert_currency(100)
    print(f"\n💹 INR (Indian Rupee):")
    print(f"  {result['original']} = {result['converted']}")
    print(f"  Rate: 1 USD = {result['rate']:.2f} INR")
    
    # Test KRW
    loc_krw = Localizer('KRW', 'metric', '24h')
    result = loc_krw.convert_currency(100)
    print(f"\n💴 KRW (Korean Won):")
    print(f"  {result['original']} = {result['converted']}")
    print(f"  Rate: 1 USD = {result['rate']:.2f} KRW")
    
    print("\n✓ All currency tests complete!")
