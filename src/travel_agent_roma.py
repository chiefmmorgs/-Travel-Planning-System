"""
Sentient Travel & Exploration Agent - ROMA Implementation
Configured for OpenRouter.ai
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CORE ROMA ARCHITECTURE
# ============================================================================

@dataclass
class TaskResult:
    """Result from an agent task execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class BaseAgent(ABC):
    """Base Agent class following ROMA architecture"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.child_agents: List[BaseAgent] = []
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        """Execute the agent's primary task"""
        pass
    
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose complex task into subtasks"""
        return []
    
    async def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """Aggregate results from child agents"""
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return TaskResult(success=False, data=None, error="All subtasks failed")
        
        return TaskResult(
            success=True,
            data={
                "aggregated_results": [r.data for r in successful_results],
                "total_subtasks": len(results),
                "successful_subtasks": len(successful_results)
            }
        )
    
    async def run(self, task: Dict[str, Any]) -> TaskResult:
        """Main execution method following ROMA pattern"""
        subtasks = await self.decompose(task)
        
        if subtasks and self.child_agents:
            print(f"[{self.name}] Decomposing into {len(subtasks)} subtasks")
            results = await self._execute_subtasks(subtasks)
            return await self.aggregate(results)
        else:
            print(f"[{self.name}] Executing directly")
            return await self.execute(task)
    
    async def _execute_subtasks(self, subtasks: List[Dict[str, Any]]) -> List[TaskResult]:
        """Execute subtasks in parallel"""
        tasks = []
        for subtask in subtasks:
            # Use agent_index if specified, otherwise round-robin
            if 'agent_index' in subtask:
                agent = self.child_agents[subtask['agent_index']]
            else:
                agent = self.child_agents[0]  # Default to first agent
            tasks.append(agent.run(subtask))
        
        return await asyncio.gather(*tasks, return_exceptions=False)


class MetaAgent(BaseAgent):
    """Meta-Agent that orchestrates other agents"""
    
    def __init__(self, name: str):
        super().__init__(name, capabilities=["orchestration", "task_decomposition"])
        
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        """Meta-agents primarily decompose, not execute directly"""
        return TaskResult(success=False, data=None, error="Meta-agent should decompose tasks")


# ============================================================================
# OPENROUTER CLIENT
# ============================================================================

class OpenRouterClient:
    """OpenRouter API client"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def generate(self, prompt: str, system: str = "You are an expert AI Travel Scout.") -> str:
        """Generate response using OpenRouter"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"


# ============================================================================
# TRAVEL-SPECIFIC AGENTS
# ============================================================================

class TravelHistoryAgent(BaseAgent):
    """Agent specialized in managing travel history"""
    
    def __init__(self):
        super().__init__(name="TravelHistoryAgent", capabilities=["history_tracking", "pattern_analysis"])
        self.history_file = "data/travel_history.json"
        self.openrouter = OpenRouterClient()
        
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        """Execute travel history tasks"""
        action = task.get("action")
        
        if action == "add_location":
            return await self._add_location(task["data"])
        elif action == "get_statistics":
            return await self._get_statistics()
        elif action == "analyze_patterns":
            return await self._analyze_patterns()
        else:
            return TaskResult(success=False, data=None, error=f"Unknown action: {action}")
    
    async def _add_location(self, location_data: Dict) -> TaskResult:
        try:
            history = self._load_history()
            history.append(location_data)
            self._save_history(history)
            return TaskResult(success=True, data=location_data)
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))
    
    async def _get_statistics(self) -> TaskResult:
        try:
            history = self._load_history()
            countries = set(loc.get("country") for loc in history if loc.get("country"))
            return TaskResult(
                success=True,
                data={
                    "total_destinations": len(history),
                    "unique_countries": len(countries),
                    "countries_list": list(countries)
                }
            )
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))
    
    async def _analyze_patterns(self) -> TaskResult:
        try:
            history = self._load_history()
            if not history:
                return TaskResult(success=True, data={"patterns": "No travel history yet."})
            
            prompt = f"""Analyze these travel patterns briefly:
{json.dumps(history, indent=2)}

Identify: preferred destination types, travel frequency, notable preferences."""
            
            response = await self.openrouter.generate(prompt)
            return TaskResult(success=True, data={"patterns": response})
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))
    
    def _load_history(self) -> List[Dict]:
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_history(self, history: List[Dict]) -> None:
        os.makedirs('data', exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)


class AdvisoryScannerAgent(BaseAgent):
    """Agent specialized in scanning travel advisories"""
    
    def __init__(self):
        super().__init__(name="AdvisoryScannerAgent", capabilities=["advisory_scanning", "safety_analysis"])
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        destination = task.get("destination", "Unknown")
        
        try:
            advisories = {
                "destination": destination,
                "risk_level": "low",
                "warnings": [],
                "recommendations": ["Stay aware of surroundings", "Keep document copies"],
                "last_updated": datetime.now().isoformat()
            }
            return TaskResult(success=True, data=advisories)
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))


class WeatherScannerAgent(BaseAgent):
    """Agent specialized in weather forecasting"""
    
    def __init__(self):
        super().__init__(name="WeatherScannerAgent", capabilities=["weather_forecasting", "climate_analysis"])
        self.api_key = os.getenv('WEATHERAPI_KEY')
        self.base_url = "http://api.weatherapi.com/v1"
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        destination = task.get("destination", "Unknown")
        days = min(task.get("days", 7), 10)
        
        if not destination or destination == "Unknown":
            return TaskResult(
                success=True,
                data={
                    "destination": "Unknown",
                    "summary": "No destination specified",
                    "current_temp": 0,
                    "note": "Destination required for weather"
                }
            )
        
        if not self.api_key:
            return TaskResult(
                success=True,
                data={
                    "destination": destination,
                    "summary": "Weather API not configured (add WEATHERAPI_KEY to .env)",
                    "current_temp": 22,
                    "current_condition": "Unknown",
                    "note": "Configure WEATHERAPI_KEY for real forecasts"
                }
            )
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/forecast.json"
                params = {"key": self.api_key, "q": destination, "days": days, "aqi": "yes"}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        location = data['location']
                        current = data['current']
                        forecast_days = data['forecast']['forecastday']
                        
                        daily_forecast = []
                        for day in forecast_days:
                            day_data = day['day']
                            daily_forecast.append({
                                'date': day['date'],
                                'condition': day_data['condition']['text'],
                                'max_temp_c': day_data['maxtemp_c'],
                                'min_temp_c': day_data['mintemp_c'],
                                'rain_chance': day_data['daily_chance_of_rain'],
                                'rain_mm': day_data['totalprecip_mm'],
                                'avg_humidity': day_data['avghumidity']
                            })
                        
                        summary_parts = [f"Currently {current['temp_c']}°C ({current['condition']['text']})"]
                        for day in daily_forecast[:3]:
                            summary_parts.append(f"{day['date']}: {day['condition']}, {day['max_temp_c']}°C/{day['min_temp_c']}°C")
                        
                        return TaskResult(
                            success=True,
                            data={
                                "destination": f"{location['name']}, {location['country']}",
                                "current_temp": current['temp_c'],
                                "current_condition": current['condition']['text'],
                                "feels_like": current['feelslike_c'],
                                "humidity": current['humidity'],
                                "wind_kph": current['wind_kph'],
                                "daily_forecast": daily_forecast,
                                "summary": " | ".join(summary_parts)
                            }
                        )
                    else:
                        # Return graceful fallback instead of failure
                        return TaskResult(
                            success=True,
                            data={
                                "destination": destination,
                                "summary": f"Weather API returned error {response.status}",
                                "current_temp": 0,
                                "note": "Weather data temporarily unavailable"
                            }
                        )
        except Exception as e:
            print(f"[WeatherScannerAgent] Error: {e}")
            # Return graceful fallback instead of failure
            return TaskResult(
                success=True,
                data={
                    "destination": destination,
                    "summary": f"Weather service error: {str(e)[:50]}",
                    "current_temp": 0,
                    "note": "Weather data temporarily unavailable"
                }
            )


class EventDiscoveryAgent(BaseAgent):
    """Agent specialized in discovering local events"""
    
    def __init__(self):
        super().__init__(name="EventDiscoveryAgent", capabilities=["event_discovery", "activity_recommendation"])
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        destination = task.get("destination", "Unknown")
        start_date = task.get("start_date")
        
        try:
            events = [
                {
                    "name": "Local Cultural Festival",
                    "date": start_date,
                    "category": "culture",
                    "description": "Experience local traditions and cuisine"
                }
            ]
            return TaskResult(success=True, data={"events": events})
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))


class BudgetAnalysisAgent(BaseAgent):
    """Agent specialized in budget analysis"""
    
    def __init__(self):
        super().__init__(name="BudgetAnalysisAgent", capabilities=["budget_tracking", "cost_optimization"])
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        trip_data = task.get("trip_data")
        
        try:
            budget = trip_data.get("budget", 0)
            duration = 7
            
            analysis = {
                "total_budget": budget,
                "estimated_daily_cost": budget / duration if duration > 0 else 0,
                "recommendations": [
                    "Book accommodations early for better rates",
                    "Consider local transportation",
                    "Look for free activities"
                ]
            }
            return TaskResult(success=True, data=analysis)
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))


class RecommendationGeneratorAgent(BaseAgent):
    """Agent that generates AI-powered recommendations"""
    
    def __init__(self):
        super().__init__(name="RecommendationGeneratorAgent", capabilities=["ai_generation", "personalization"])
        self.openrouter = OpenRouterClient()
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        context = task.get("context", {})
        
        try:
            prompt = self._build_prompt(context)
            recommendations = await self.openrouter.generate(prompt)
            
            return TaskResult(
                success=True,
                data={
                    "recommendations": recommendations,
                    "generated_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return TaskResult(success=False, data=None, error=str(e))
    
    def _build_prompt(self, context: Dict) -> str:
        return f"""As an AI Travel Scout, generate personalized travel recommendations.

Context:
{json.dumps(context, indent=2)}

Generate a friendly weekly travel digest that includes:
1. 2-3 destination recommendations based on travel history
2. Planning tips for upcoming trips with specific weather details
3. Budget insights
4. Unique experiences to consider

Keep it concise and actionable."""


# ============================================================================
# META-AGENTS
# ============================================================================

class TripIntelligenceAgent(MetaAgent):
    """Meta-Agent that coordinates intelligence gathering for a trip"""
    
    def __init__(self):
        super().__init__(name="TripIntelligenceAgent")
        self.advisory_agent = AdvisoryScannerAgent()
        self.weather_agent = WeatherScannerAgent()
        self.events_agent = EventDiscoveryAgent()
        try:
            from agents.destination_discovery_agent import DestinationDiscoveryAgent
            self.destination_agent = DestinationDiscoveryAgent()
            self.child_agents = [self.advisory_agent, self.weather_agent, self.events_agent, self.destination_agent]
        except:
            self.child_agents = [self.advisory_agent, self.weather_agent, self.events_agent]
    
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        destination = task.get("destination", "Unknown")
        start_date = task.get("start_date")
        end_date = task.get("end_date")
        
        print(f"[TripIntelligenceAgent] Gathering intelligence for: {destination}")
        
        subtasks = [
            {"agent_index": 0, "destination": destination},  # Advisory
            {"agent_index": 1, "destination": destination, "days": 7},  # Weather
            {"agent_index": 2, "destination": destination, "start_date": start_date, "end_date": end_date}  # Events
        ]
        
        # Add destination discovery if available
        if len(self.child_agents) > 3:
            subtasks.append({
                "agent_index": 3,
                "destination": destination,
                "budget": task.get("budget", 2000),
                "travel_style": task.get("travel_style", "cultural")
            })
        
        return subtasks
    
    async def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """Aggregate intelligence - includes ALL results, even partial failures"""
        intelligence = {}
        
        # Merge all data, even from failed attempts
        for result in results:
            if result.data:  # Include data from both success and failure
                intelligence.update(result.data)
        
        return TaskResult(
            success=True,
            data={
                "intelligence": intelligence,
                "scans_completed": len([r for r in results if r.success])
            }
        )


class TravelDigestMetaAgent(MetaAgent):
    """Top-level Meta-Agent that orchestrates weekly travel digest generation"""
    
    def __init__(self):
        super().__init__(name="TravelDigestMetaAgent")
        
        self.history_agent = TravelHistoryAgent()
        self.intelligence_agent = TripIntelligenceAgent()
        self.recommendation_agent = RecommendationGeneratorAgent()
        self.budget_agent = BudgetAnalysisAgent()
        
        self.child_agents = [
            self.history_agent,
            self.intelligence_agent,
            self.budget_agent,
            self.recommendation_agent
        ]
    
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        upcoming_trips = task.get("upcoming_trips", [])
        
        subtasks = []
        
        # History tasks
        subtasks.append({"agent_index": 0, "action": "get_statistics"})
        subtasks.append({"agent_index": 0, "action": "analyze_patterns"})
        
        # Trip-specific tasks
        for trip in upcoming_trips:
            subtasks.append({
                "agent_index": 1,  # intelligence_agent
                "destination": trip.get("destination"),
                "start_date": trip.get("start_date"),
                "end_date": trip.get("end_date")
            })
            
            subtasks.append({
                "agent_index": 2,  # budget_agent
                "trip_data": trip
            })
        
        return subtasks
    
    async def aggregate(self, results: List[TaskResult]) -> TaskResult:
        context = {"history": {}, "intelligence": [], "budget": []}
        
        for result in results:
            if result.success:
                data_str = str(result.data)
                if "total_destinations" in data_str:
                    context["history"]["stats"] = result.data
                elif "patterns" in data_str:
                    context["history"]["patterns"] = result.data
                elif "intelligence" in data_str:
                    context["intelligence"].append(result.data)
                elif "total_budget" in data_str:
                    context["budget"].append(result.data)
        
        final_task = {"context": context}
        recommendation_result = await self.recommendation_agent.run(final_task)
        
        return TaskResult(
            success=True,
            data={
                "digest": recommendation_result.data,
                "context": context,
                "generated_at": datetime.now().isoformat()
            }
        )


# ============================================================================
# MAIN INTERFACE
# ============================================================================

class SentientTravelAgent:
    """Main interface for the Sentient Travel Agent"""
    
    def __init__(self):
        self.meta_agent = TravelDigestMetaAgent()
        self.upcoming_trips = []
        
    def add_trip(self, destination: str, start_date: str, end_date: str, 
                 budget: float, travel_style: str = "cultural") -> None:
        trip = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "travel_style": travel_style
        }
        self.upcoming_trips.append(trip)
        print(f"✓ Added trip to {destination}")
    
    async def generate_weekly_digest(self) -> Dict[str, Any]:
        print("\n🔍 Generating weekly digest with ROMA architecture...\n")
        
        task = {"type": "weekly_digest", "upcoming_trips": self.upcoming_trips}
        result = await self.meta_agent.run(task)
        
        if result.success:
            print("\n✓ Digest generated successfully!\n")
            return result.data
        else:
            print(f"\n✗ Error: {result.error}")
            return {}


async def main():
    print("="*60)
    print("🌍 SENTIENT TRAVEL AGENT - ROMA ARCHITECTURE")
    print("="*60)
    
    agent = SentientTravelAgent()
    agent.add_trip("Bali, Indonesia", "2025-12-01", "2025-12-10", 3000, "adventure")
    
    digest = await agent.generate_weekly_digest()
    print(json.dumps(digest, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
