"""
Flight Search System with Provider Abstraction
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class FlightQuery:
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str]
    cabin: str
    passengers: int
    budget: Optional[float]
    nonstop: bool
    preferences: Dict

@dataclass
class FlightSegment:
    origin: str
    destination: str
    departure: str
    arrival: str
    airline: str
    flight_number: str
    duration_min: int

@dataclass
class FlightOption:
    provider: str
    price: Optional[float]
    currency: str
    duration_min: int
    stops: int
    segments: List[FlightSegment]
    baggage: str
    refundable: bool
    co2_kg: Optional[float]
    score: float
    rank_reason: str

@dataclass
class CityHint:
    iata: str
    city: str
    country: str
    rationale: str

@dataclass
class CitySnapshot:
    city: str
    summary: str
    attractions: List[str]
    history_hook: str


class FlightProvider:
    def search(self, query: FlightQuery) -> List[FlightOption]:
        raise NotImplementedError


class MockFlightProvider(FlightProvider):
    def __init__(self):
        self.airlines = {
            'economy': ['United', 'Delta', 'American'],
            'premium': ['Virgin Atlantic', 'Lufthansa'],
            'business': ['Emirates', 'Qatar'],
            'first': ['Emirates', 'Singapore Airlines']
        }
    
    def search(self, query: FlightQuery) -> List[FlightOption]:
        options = []
        base_prices = {'economy': 500, 'premium': 1200, 'business': 3500, 'first': 8000}
        base_price = base_prices.get(query.cabin, 500)
        
        options.append(self._create_option(query, base_price * 1.3, 0, 480, 'Fastest', True, 150))
        options.append(self._create_option(query, base_price * 0.9, 1, 600, 'Balanced', False, 180))
        options.append(self._create_option(query, base_price * 0.7, 2, 780, 'Cheapest', False, 200))
        
        return options
    
    def _create_option(self, query, price, stops, duration, label, refundable, co2):
        segments = []
        airline = self.airlines.get(query.cabin, self.airlines['economy'])[0]
        
        if stops == 0:
            segments.append(FlightSegment(
                origin=query.origin,
                destination=query.destination,
                departure=query.departure_date + 'T08:00',
                arrival=query.departure_date + 'T16:00',
                airline=airline,
                flight_number=f'{airline[:2].upper()}123',
                duration_min=duration
            ))
        else:
            leg_duration = duration // (stops + 1)
            segments.append(FlightSegment(
                origin=query.origin,
                destination='HUB',
                departure=query.departure_date + 'T08:00',
                arrival=query.departure_date + 'T12:00',
                airline=airline,
                flight_number=f'{airline[:2].upper()}123',
                duration_min=leg_duration
            ))
            segments.append(FlightSegment(
                origin='HUB',
                destination=query.destination,
                departure=query.departure_date + 'T14:00',
                arrival=query.departure_date + 'T18:00',
                airline=airline,
                flight_number=f'{airline[:2].upper()}456',
                duration_min=leg_duration
            ))
        
        score = self._calculate_score(price, duration, stops, query.budget, refundable)
        
        return FlightOption(
            provider='Mock',
            price=price * query.passengers,
            currency='USD',
            duration_min=duration,
            stops=stops,
            segments=segments,
            baggage='2 bags' if query.cabin in ['business', 'first'] else '1 bag',
            refundable=refundable,
            co2_kg=co2 * query.passengers,
            score=score,
            rank_reason=label
        )
    
    def _calculate_score(self, price, duration, stops, budget, refundable):
        price_score = 1.0 - min(price / 10000, 1.0)
        duration_score = 1.0 - min(duration / 1440, 1.0)
        stops_score = 1.0 - (stops / 3)
        perks_score = 0.1 if refundable else 0.0
        
        score = (price_score * 0.55 + duration_score * 0.25 + stops_score * 0.15 + perks_score * 0.05)
        
        if budget and price > budget:
            score *= 0.7
        
        return round(score, 3)


class RouteHeuristics:
    def __init__(self):
        self.entry_cities = {
            'japan': [
                CityHint('NRT', 'Tokyo', 'Japan', 'Main international gateway'),
                CityHint('KIX', 'Osaka', 'Japan', 'Alternative, lower cost'),
            ],
            'south korea': [
                CityHint('ICN', 'Seoul', 'South Korea', 'Primary hub'),
                CityHint('PUS', 'Busan', 'South Korea', 'Secondary gateway'),
            ],
            'india': [
                CityHint('DEL', 'Delhi', 'India', 'Main hub'),
                CityHint('BOM', 'Mumbai', 'India', 'West coast gateway'),
                CityHint('BLR', 'Bangalore', 'India', 'South India entry'),
            ],
            'france': [
                CityHint('CDG', 'Paris', 'France', 'Primary European hub'),
                CityHint('NCE', 'Nice', 'France', 'South France'),
            ],
            'nigeria': [
                CityHint('LOS', 'Lagos', 'Nigeria', 'Main business hub'),
                CityHint('ABV', 'Abuja', 'Nigeria', 'Capital city'),
            ],
            'kenya': [
                CityHint('NBO', 'Nairobi', 'Kenya', 'East Africa hub'),
                CityHint('MBA', 'Mombasa', 'Kenya', 'Coastal entry'),
            ],
            'brazil': [
                CityHint('GRU', 'São Paulo', 'Brazil', 'Main gateway'),
                CityHint('GIG', 'Rio de Janeiro', 'Brazil', 'Tourist hub'),
            ],
        }
    
    def suggest_entry_cities(self, destination_country, user_city=None):
        country_lower = destination_country.lower()
        
        if user_city:
            hints = self.entry_cities.get(country_lower, [])
            for hint in hints:
                if user_city.lower() in hint.city.lower():
                    return [hint] + [h for h in hints if h != hint]
        
        return self.entry_cities.get(country_lower, [
            CityHint('XXX', destination_country, destination_country, 'Default entry')
        ])[:3]


class WikipediaEnricher:
    def get_city_snapshot(self, city):
        try:
            headers = {'User-Agent': 'SentientTravelAgent/1.0 (Educational)'}
            
            response = requests.get(
                'https://en.wikipedia.org/w/api.php',
                params={
                    'action': 'query',
                    'format': 'json',
                    'titles': city,
                    'prop': 'extracts',
                    'exintro': True,
                    'explaintext': True,
                },
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            pages = data['query']['pages']
            page = list(pages.values())[0]
            
            summary = page.get('extract', f'{city} is a major destination.')
            if len(summary) > 300:
                summary = summary[:300] + '...'
            
            attractions = self._get_attractions(city)
            history_hook = self._extract_history(summary)
            
            return CitySnapshot(
                city=city,
                summary=summary,
                attractions=attractions,
                history_hook=history_hook
            )
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return CitySnapshot(
                city=city,
                summary=f"{city} is a major destination.",
                attractions=[f"{city} attractions"],
                history_hook=f"Rich history of {city}"
            )
    
    def _get_attractions(self, city):
        mock_attractions = {
            'Tokyo': [
                'Senso-ji Temple - Ancient Buddhist temple',
                'Tokyo Skytree - Tallest structure in Japan',
                'Shibuya Crossing - Iconic intersection',
                'Meiji Shrine - Peaceful Shinto shrine',
                'Tsukiji Market - Fresh seafood paradise'
            ],
            'Seoul': [
                'Gyeongbokgung Palace - Grand royal palace',
                'N Seoul Tower - Panoramic city views',
                'Bukchon Hanok Village - Traditional houses',
                'Myeongdong - Shopping and street food',
                'Dongdaemun Design Plaza - Architecture'
            ],
            'Delhi': [
                'Red Fort - Mughal fortress',
                'India Gate - War memorial',
                'Lotus Temple - Bahai temple',
                'Qutub Minar - Ancient minaret',
                'Humayuns Tomb - Garden tomb'
            ]
        }
        return mock_attractions.get(city, [f"Popular {city} sights"])
    
    def _extract_history(self, summary):
        import re
        sentences = summary.split('.')
        for sent in sentences:
            if re.search(r'\d{3,4}', sent):
                return sent.strip() + '.'
        return sentences[0] + '.' if sentences else "Rich historical heritage."


class FlightSearchOrchestrator:
    def __init__(self):
        self.route_hints = RouteHeuristics()
        self.wiki = WikipediaEnricher()
        self.provider = MockFlightProvider()
        print("Using mock flight provider")
    
    def search_and_rank(self, query):
        entry_cities = self.route_hints.suggest_entry_cities(query.destination, None)
        options = self.provider.search(query)
        ranked_options = sorted(options, key=lambda x: x.score, reverse=True)
        
        if ranked_options:
            cheapest_idx = min(range(len(ranked_options)), 
                             key=lambda i: ranked_options[i].price or float('inf'))
            ranked_options[cheapest_idx].rank_reason = 'Cheapest'
            
            fastest_idx = min(range(len(ranked_options)), 
                            key=lambda i: ranked_options[i].duration_min)
            ranked_options[fastest_idx].rank_reason = 'Fastest'
            
            if ranked_options[0] != ranked_options[cheapest_idx] and \
               ranked_options[0] != ranked_options[fastest_idx]:
                ranked_options[0].rank_reason = 'Balanced'
        
        city_snapshot = None
        if entry_cities:
            city_snapshot = self.wiki.get_city_snapshot(entry_cities[0].city)
        
        google_link = self._generate_google_flights_link(query, entry_cities[0] if entry_cities else None)
        
        return {
            'query': asdict(query),
            'entry_cities': [asdict(c) for c in entry_cities],
            'options': [asdict(opt) for opt in ranked_options[:6]],
            'city_snapshot': asdict(city_snapshot) if city_snapshot else None,
            'google_flights_link': google_link
        }
    
    def _generate_google_flights_link(self, query, entry_city):
        dest_code = entry_city.iata if entry_city else query.destination
        link = f"https://www.google.com/travel/flights?q=flights%20to%20{dest_code}%20from%20{query.origin}"
        if query.departure_date:
            link += f"%20on%20{query.departure_date}"
        if query.return_date:
            link += f"%20return%20{query.return_date}"
        link += f"&curr=USD&tfs=CAEQAg"
        return link


if __name__ == "__main__":
    print("Testing Flight Search System\n")
    
    orchestrator = FlightSearchOrchestrator()
    
    query = FlightQuery(
        origin='JFK',
        destination='Japan',
        departure_date='2025-11-15',
        return_date='2025-11-25',
        cabin='economy',
        passengers=2,
        budget=2000,
        nonstop=False,
        preferences={'red_eye_avoid': True}
    )
    
    print(f"Searching flights: {query.origin} -> {query.destination}")
    print(f"Dates: {query.departure_date} to {query.return_date}")
    print(f"Passengers: {query.passengers}, Cabin: {query.cabin}\n")
    
    result = orchestrator.search_and_rank(query)
    
    print("Entry Cities:")
    for city in result['entry_cities']:
        print(f"  {city['city']} ({city['iata']}) - {city['rationale']}")
    
    print(f"\nFound {len(result['options'])} flight options:")
    for i, opt in enumerate(result['options'][:3], 1):
        print(f"\n{i}. {opt['rank_reason']} - ${opt['price']:.2f}")
        print(f"   Duration: {opt['duration_min']//60}h {opt['duration_min']%60}m")
        print(f"   Stops: {opt['stops']}")
        print(f"   Score: {opt['score']}")
    
    if result['city_snapshot']:
        snap = result['city_snapshot']
        print(f"\nCity Snapshot: {snap['city']}")
        print(f"Summary: {snap['summary'][:100]}...")
        print(f"Top Attraction: {snap['attractions'][0]}")
    
    print(f"\nGoogle Flights: {result['google_flights_link']}")
