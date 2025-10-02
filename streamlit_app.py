from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from datetime import datetime
from src.trip_manager import TripManager
from src.agents import TravelDigestMetaAgent
from src.localization import Localizer
from src.flight_search import FlightSearchOrchestrator, FlightQuery, WikipediaEnricher
import json

st.set_page_config(page_title="Travel Planning System", page_icon="��", layout="wide")

# Initialize
if 'trip_mgr' not in st.session_state:
    st.session_state.trip_mgr = TripManager()
if 'digest_agent' not in st.session_state:
    st.session_state.digest_agent = TravelDigestMetaAgent()
if 'flight_orchestrator' not in st.session_state:
    st.session_state.flight_orchestrator = FlightSearchOrchestrator()
if 'wiki_enricher' not in st.session_state:
    st.session_state.wiki_enricher = WikipediaEnricher()

trip_mgr = st.session_state.trip_mgr
digest_agent = st.session_state.digest_agent
flight_orch = st.session_state.flight_orchestrator
wiki = st.session_state.wiki_enricher

# Header
st.title("🌍 Complete Travel Planning System")
st.markdown("Real-time currency conversion | Smart itineraries | Full localization")

# Sidebar - Profile
st.sidebar.header("Your Profile")
profile = trip_mgr.load_user_profile()

with st.sidebar.form("profile_form"):
    name = st.text_input("Name", value=profile.get('name', ''))
    home_country = st.text_input("Home Country", value=profile.get('home_country', 'Nigeria'))
    profession = st.text_input("Profession", value=profile.get('profession', ''))
    interests = st.multiselect(
        "Travel Interests",
        ["Culture", "Adventure", "Food", "Nature", "History", "Nightlife", "Shopping", "Relaxation"],
        default=profile.get('interests', ["Culture", "Adventure"])
    )
    
    if st.form_submit_button("Save Profile"):
        trip_mgr.save_user_profile({
            "name": name,
            "home_country": home_country,
            "profession": profession,
            "interests": interests
        })
        st.success("Saved")

st.sidebar.divider()

# Settings
st.sidebar.header("Settings")
currency = st.sidebar.selectbox("Currency", ["NGN", "USD", "EUR", "GBP"], index=0)
units = st.sidebar.selectbox("Units", ["Metric", "Imperial"], index=0).lower()
time_format = st.sidebar.selectbox("Time Format", ["24h", "12h"], index=0)

if 'localizer' not in st.session_state or st.session_state.get('currency') != currency:
    st.session_state.localizer = Localizer(currency, units, time_format)
    st.session_state.currency = currency

localizer = st.session_state.localizer
st.sidebar.caption(f"Rates: {localizer.last_updated}")

st.sidebar.divider()

# Advanced
st.sidebar.subheader("Advanced")
with st.sidebar.expander("API Status"):
    apis = {
        "OpenRouter": bool(os.getenv('OPENROUTER_API_KEY')),
        "Weather": bool(os.getenv('OPENWEATHER_API_KEY')),
        "Events": bool(os.getenv('PREDICTHQ_API_KEY')),
        "Exchange": bool(localizer.exchange_rates)
    }
    for api, status in apis.items():
        st.write(f"{'✅' if status else '❌'} {api}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Add Trip", "My Trips", "Localization", "🛫 Flight Search"
])

# Tab 1: Add Trip
with tab1:
    st.subheader("Add New Trip")
    
    with st.form("add_trip_form"):
        destination = st.text_input("Destination")
        budget = st.number_input("Budget (USD)", min_value=0, value=1000)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if st.form_submit_button("Add Trip", type="primary"):
            trip = {
                "destination": destination,
                "budget": budget,
                "start_date": str(start_date),
                "end_date": str(end_date)
            }
            trip_mgr.save_trip(trip)
            st.success(f"Added trip to {destination}")
            st.rerun()

# Tab 2: My Trips (Individual Intelligence Reports)
with tab2:
    st.subheader("My Trips")
    
    trips = trip_mgr.load_trips()
    
    if trips:
        for i, trip in enumerate(trips):
            with st.container():
                st.markdown(f"### 📍 {trip['destination']} - ${trip['budget']}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.caption(f"Start: {trip['start_date']}")
                with col2:
                    st.caption(f"End: {trip.get('end_date', 'Not set')}")
                with col3:
                    if st.button("🔍 Analyze", key=f"analyze_{i}", type="primary"):
                        with st.spinner(f"Analyzing {trip['destination']}..."):
                            # Get intelligence
                            intel = digest_agent.trip_intel_agent.execute(
                                trip['destination'],
                                float(trip['budget']),
                                7
                            )
                            
                            # Get city guide
                            city_snapshot = wiki.get_city_snapshot(trip['destination'])
                            
                            # Get AI recommendation
                            rec_context = {
                                'destination': trip['destination'],
                                'budget': str(trip['budget']),
                                'interests': profile.get('interests', []),
                                'weather_summary': intel['weather_forecast']['condition'],
                                'events_summary': f"{intel['local_events']['event_count']} events",
                                'advisory_level': intel['safety_advisory']['safety_level']
                            }
                            recommendation = digest_agent.recommendation_agent.execute(rec_context)
                            
                            # Store
                            st.session_state[f'intel_{i}'] = {
                                'intelligence': intel,
                                'city_guide': city_snapshot,
                                'recommendation': recommendation
                            }
                        st.rerun()
                
                # Show intelligence if generated
                if f'intel_{i}' in st.session_state:
                    data = st.session_state[f'intel_{i}']
                    
                    # City Guide
                    with st.expander(f"📖 {data['city_guide'].city} Guide", expanded=True):
                        st.write(data['city_guide'].summary)
                        
                        st.markdown("**Top Attractions**")
                        for j, attr in enumerate(data['city_guide'].attractions[:5], 1):
                            st.markdown(f"{j}. {attr}")
                        
                        st.info(f"**History:** {data['city_guide'].history_hook}")
                    
                    # Intelligence
                    intel = data['intelligence']
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**💰 Budget**")
                        budget_info = intel['budget_analysis']
                        st.metric("Daily Cost", f"${budget_info['daily_cost']:.2f}")
                        st.progress(min(budget_info['feasibility_percentage'] / 100, 1.0))
                        st.caption(f"Feasibility: {budget_info['feasibility_percentage']:.0f}%")
                        
                        st.markdown("**🌤️ Weather**")
                        weather = intel['weather_forecast']
                        st.metric("Temperature", f"{weather['avg_temp']}°C")
                        st.caption(f"Condition: {weather['condition']}")
                    
                    with col_b:
                        st.markdown("**🛡️ Safety**")
                        advisory = intel['safety_advisory']
                        st.info(f"{advisory['safety_level']}")
                        st.caption(advisory['advisory_message'])
                        
                        st.markdown("**🎉 Events**")
                        events = intel['local_events']
                        st.metric("Events Found", events['event_count'])
                        if events.get('events'):
                            for event in events['events'][:3]:
                                st.caption(f"• {event['title']}")
                    
                    # AI Recommendation
                    st.markdown("**🤖 AI Recommendation**")
                    st.markdown(data['recommendation']['recommendation'])
                
                st.divider()
    else:
        st.info("No trips yet. Add your first trip in the 'Add Trip' tab!")

# Tab 3: Localization
with tab3:
    st.subheader("Currency & Localization")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Currency", localizer.user_currency)
        if st.button("Refresh Rates"):
            localizer.fetch_exchange_rates()
            st.rerun()
    with col2:
        st.metric("Units", localizer.units)
    with col3:
        st.metric("Time", localizer.time_format)
    
    st.markdown("---")
    st.markdown("**Exchange Rates**")
    
    for curr in ['USD', 'EUR', 'GBP', 'NGN', 'INR', 'JPY', 'KRW']:
        if curr in localizer.exchange_rates:
            rate = localizer.exchange_rates[curr]
            st.write(f"1 USD = {rate:.2f} {curr}")
    
    st.markdown("---")
    st.markdown("**Budget Conversions**")
    
    trips = trip_mgr.load_trips()
    if trips:
        for trip in trips:
            with st.expander(f"{trip['destination']}"):
                converted = localizer.convert_currency(trip['budget'])
                st.write(f"**Total:** {converted['converted']}")
                
                import re
                numeric = re.sub(r'[^\d.,]', '', converted['converted']).replace(',', '')
                daily = float(numeric) / 7
                st.write(f"**Daily:** {localizer.user_currency} {daily:,.2f}")

# Tab 4: Flight Search
with tab4:
    st.subheader("Flight Search & Entry City Optimizer")
    
    with st.form("flight_search"):
        col1, col2 = st.columns(2)
        
        with col1:
            origin = st.text_input("Origin", "JFK")
            destination = st.text_input("Destination", "Japan")
            departure = st.date_input("Departure")
            return_date = st.date_input("Return", value=None)
        
        with col2:
            cabin = st.selectbox("Cabin", ["economy", "premium", "business", "first"])
            passengers = st.number_input("Passengers", 1, 9, 1)
            budget = st.number_input("Budget (USD)", 0, 20000, 2000, 100)
            nonstop = st.checkbox("Nonstop only")
        
        if st.form_submit_button("Search Flights", type="primary"):
            with st.spinner("Searching..."):
                query = FlightQuery(
                    origin=origin.upper(),
                    destination=destination,
                    departure_date=departure.strftime('%Y-%m-%d'),
                    return_date=return_date.strftime('%Y-%m-%d') if return_date else None,
                    cabin=cabin,
                    passengers=passengers,
                    budget=budget if budget > 0 else None,
                    nonstop=nonstop,
                    preferences={}
                )
                
                results = flight_orch.search_and_rank(query)
                st.session_state.flight_results = results
            st.success(f"Found {len(results['options'])} options")
    
    if 'flight_results' in st.session_state:
        results = st.session_state.flight_results
        
        result_tabs = st.tabs(["Options", "Entry Cities", "City Guide"])
        
        with result_tabs[0]:
            for i, opt in enumerate(results['options'], 1):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    colors = {'Cheapest': 'green', 'Fastest': 'blue', 'Balanced': 'orange'}
                    color = colors.get(opt['rank_reason'], 'gray')
                    st.markdown(f"**{i}. {opt['rank_reason']}** :{color}[{opt['rank_reason']}]")
                
                with col2:
                    st.metric("Price", f"${opt['price']:,.0f}")
                
                with col3:
                    h = opt['duration_min'] // 60
                    m = opt['duration_min'] % 60
                    st.metric("Time", f"{h}h {m}m")
                
                with col4:
                    stops = "Direct" if opt['stops'] == 0 else f"{opt['stops']} stops"
                    st.metric("Stops", stops)
                
                with st.expander("Details"):
                    st.write(f"Baggage: {opt['baggage']} | Refundable: {'Yes' if opt['refundable'] else 'No'}")
                    st.progress(opt['score'])
                
                st.divider()
            
            if results.get('google_flights_link'):
                st.link_button("Open in Google Flights", results['google_flights_link'])
        
        with result_tabs[1]:
            for city in results['entry_cities']:
                st.markdown(f"**{city['city']}** ({city['iata']})")
                st.caption(city['rationale'])
                st.divider()
        
        with result_tabs[2]:
            if results.get('city_snapshot'):
                snap = results['city_snapshot']
                st.markdown(f"### {snap['city']}")
                st.write(snap['summary'])
                st.markdown("**Attractions**")
                for i, attr in enumerate(snap['attractions'], 1):
                    st.markdown(f"{i}. {attr}")
                st.info(snap['history_hook'])
