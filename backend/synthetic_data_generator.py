"""
Synthetic data generator for the Climate-Resilient Healthcare System
Creates realistic climate and health data for India with seasonal patterns
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize faker
fake = Faker('en_IN')

# Constants
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
OUTPUT_FILE = os.path.join(DATA_DIR, "synthetic_climate_health_2023.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Indian cities with their climate characteristics
INDIAN_CITIES = [
    {"name": "Delhi", "temp_base": 25, "temp_var": 15, "rain_base": 30, "rain_var": 100, 
     "humidity_base": 50, "humidity_var": 30, "wind_base": 5, "wind_var": 20, 
     "pm25_base": 100, "pm25_var": 150, "population": 16.8},
    {"name": "Mumbai", "temp_base": 27, "temp_var": 8, "rain_base": 200, "rain_var": 300, 
     "humidity_base": 70, "humidity_var": 20, "wind_base": 8, "wind_var": 25, 
     "pm25_base": 60, "pm25_var": 80, "population": 12.5},
    {"name": "Kolkata", "temp_base": 26, "temp_var": 10, "rain_base": 150, "rain_var": 200, 
     "humidity_base": 75, "humidity_var": 15, "wind_base": 6, "wind_var": 15, 
     "pm25_base": 80, "pm25_var": 100, "population": 4.5},
    {"name": "Chennai", "temp_base": 29, "temp_var": 7, "rain_base": 120, "rain_var": 250, 
     "humidity_base": 70, "humidity_var": 20, "wind_base": 7, "wind_var": 20, 
     "pm25_base": 50, "pm25_var": 70, "population": 4.6},
    {"name": "Bangalore", "temp_base": 24, "temp_var": 6, "rain_base": 80, "rain_var": 150, 
     "humidity_base": 65, "humidity_var": 25, "wind_base": 5, "wind_var": 15, 
     "pm25_base": 40, "pm25_var": 60, "population": 8.4},
    {"name": "Hyderabad", "temp_base": 26, "temp_var": 8, "rain_base": 70, "rain_var": 150, 
     "humidity_base": 60, "humidity_var": 25, "wind_base": 6, "wind_var": 18, 
     "pm25_base": 55, "pm25_var": 75, "population": 6.8},
    {"name": "Ahmedabad", "temp_base": 28, "temp_var": 12, "rain_base": 50, "rain_var": 120, 
     "humidity_base": 55, "humidity_var": 30, "wind_base": 7, "wind_var": 20, 
     "pm25_base": 70, "pm25_var": 90, "population": 5.6},
    {"name": "Pune", "temp_base": 25, "temp_var": 9, "rain_base": 60, "rain_var": 140, 
     "humidity_base": 60, "humidity_var": 25, "wind_base": 5, "wind_var": 15, 
     "pm25_base": 50, "pm25_var": 70, "population": 3.1},
    {"name": "Jaipur", "temp_base": 27, "temp_var": 14, "rain_base": 40, "rain_var": 100, 
     "humidity_base": 45, "humidity_var": 30, "wind_base": 8, "wind_var": 22, 
     "pm25_base": 80, "pm25_var": 100, "population": 3.0},
    {"name": "Lucknow", "temp_base": 26, "temp_var": 13, "rain_base": 60, "rain_var": 120, 
     "humidity_base": 55, "humidity_var": 30, "wind_base": 5, "wind_var": 15, 
     "pm25_base": 90, "pm25_var": 120, "population": 2.8}
]

# Seasonal patterns for India (monthly adjustments)
SEASONAL_PATTERNS = {
    # Month: [temp_adj, rain_adj, humidity_adj, wind_adj, pm25_adj]
    1: [-5, -50, -10, 0, 30],    # January: Cold, dry, polluted
    2: [-3, -45, -5, 5, 20],     # February: Cold to mild, dry
    3: [0, -40, -5, 10, 10],     # March: Warming up
    4: [5, -30, -10, 15, 0],     # April: Hot, dry, windy
    5: [10, -20, -15, 10, -10],  # May: Very hot, pre-monsoon
    6: [8, 50, 10, 5, -20],      # June: Hot, monsoon starts
    7: [5, 100, 15, 0, -30],     # July: Monsoon peak
    8: [4, 80, 15, -5, -30],     # August: Monsoon continues
    9: [3, 40, 10, -10, -20],    # September: Monsoon ending
    10: [0, -10, 0, -5, 0],      # October: Post-monsoon
    11: [-2, -30, -5, -5, 10],   # November: Cooling
    12: [-4, -40, -10, 0, 20]    # December: Cold, dry, polluted
}

# Special events (cyclones, heatwaves, etc.) - will be randomly inserted
SPECIAL_EVENTS = [
    {"name": "Cyclone", "duration": 5, "temp_adj": -5, "rain_adj": 300, "humidity_adj": 20, "wind_adj": 40, "pm25_adj": -20},
    {"name": "Heatwave", "duration": 10, "temp_adj": 8, "rain_adj": -30, "humidity_adj": -15, "wind_adj": 5, "pm25_adj": 30},
    {"name": "Severe Air Pollution", "duration": 7, "temp_adj": -2, "rain_adj": -40, "humidity_adj": -10, "wind_adj": -10, "pm25_adj": 200},
    {"name": "Drought", "duration": 30, "temp_adj": 6, "rain_adj": -50, "humidity_adj": -20, "wind_adj": 10, "pm25_adj": 40},
    {"name": "Urban Flooding", "duration": 3, "temp_adj": -3, "rain_adj": 200, "humidity_adj": 15, "wind_adj": 15, "pm25_adj": -10}
]

# Health impact formulas
def calculate_health_impacts(temp, rain, humidity, wind, pm25, event_name=None, population=1.0):
    """Calculate health impacts based on climate variables"""
    # Base calculations with some randomness
    noise = lambda: np.random.normal(1, 0.2)  # 20% noise factor
    
    # Population scaling factor (in millions)
    pop_scale = population / 10.0
    
    # Base health impacts
    heat_stress_cases = max(0, (temp - 30) * 0.3 * noise() * pop_scale) if temp > 30 else 0
    flood_injuries = max(0, (rain - 50) * 0.05 * noise() * pop_scale) if rain > 50 else 0
    resp_issues = max(0, pm25 * 0.02 * noise() * pop_scale)
    vector_diseases = max(0, (temp * 0.1 + rain * 0.02 + humidity * 0.01) * noise() * pop_scale)
    waterborne = max(0, rain * 0.04 * noise() * pop_scale) if rain > 30 else 0
    mental_health = max(0, ((temp > 35) * 10 + (rain > 100) * 15) * noise() * pop_scale)
    
    # Emergency calls based on overall risk
    total_risk = heat_stress_cases + flood_injuries + resp_issues + vector_diseases + waterborne
    emergency_calls = max(0, total_risk * 0.3 * noise())
    
    # Event-specific adjustments
    if event_name:
        if event_name == "Cyclone":
            flood_injuries *= 3
            emergency_calls *= 5
            mental_health *= 2
        elif event_name == "Heatwave":
            heat_stress_cases *= 4
            mental_health *= 1.5
        elif event_name == "Severe Air Pollution":
            resp_issues *= 5
            mental_health *= 1.2
        elif event_name == "Drought":
            waterborne *= 0.5
            mental_health *= 2
        elif event_name == "Urban Flooding":
            flood_injuries *= 4
            waterborne *= 3
            emergency_calls *= 3
    
    # Calculate capacity needs
    beds_needed = max(10, int((heat_stress_cases + flood_injuries + resp_issues + vector_diseases + waterborne) * 0.2))
    staff_needed = max(5, int(beds_needed * 0.6))
    icu_needed = max(2, int(beds_needed * 0.15))
    ventilators_needed = max(1, int(beds_needed * 0.08))
    ambulances_needed = max(1, int(emergency_calls * 0.1))
    
    # Economic impact (in thousands of rupees)
    economic_cost = int((heat_stress_cases * 5 + flood_injuries * 8 + resp_issues * 6 + 
                     vector_diseases * 10 + waterborne * 4 + mental_health * 2) * 1000)
    
    # Sustainability metrics
    energy_usage = beds_needed * 15  # kWh per day
    water_usage = beds_needed * 300  # liters per day
    waste_generated = beds_needed * 2  # kg per day
    
    return {
        "heat_stress_cases": round(heat_stress_cases, 1),
        "flood_injuries": round(flood_injuries, 1),
        "resp_issues": round(resp_issues, 1),
        "vector_diseases": round(vector_diseases, 1),
        "waterborne_diseases": round(waterborne, 1),
        "mental_health_cases": round(mental_health, 1),
        "emergency_calls": round(emergency_calls, 1),
        "beds_needed": beds_needed,
        "staff_needed": staff_needed,
        "icu_needed": icu_needed,
        "ventilators_needed": ventilators_needed,
        "ambulances_needed": ambulances_needed,
        "economic_cost": economic_cost,
        "energy_usage": energy_usage,
        "water_usage": water_usage,
        "waste_generated": waste_generated
    }

def generate_synthetic_data(start_date="2023-01-01", days=365):
    """Generate synthetic climate and health data for Indian cities"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    dates = [start + timedelta(days=i) for i in range(days)]
    
    # Prepare to store data
    all_data = []
    
    # Generate special events (random timing)
    events = {}
    for city in INDIAN_CITIES:
        events[city["name"]] = []
        # Each city gets 1-3 random events
        for _ in range(random.randint(1, 3)):
            event = random.choice(SPECIAL_EVENTS)
            start_day = random.randint(0, days - event["duration"])
            end_day = start_day + event["duration"]
            events[city["name"]].append({
                "event": event["name"],
                "start": start_day,
                "end": end_day,
                "temp_adj": event["temp_adj"],
                "rain_adj": event["rain_adj"],
                "humidity_adj": event["humidity_adj"],
                "wind_adj": event["wind_adj"],
                "pm25_adj": event["pm25_adj"]
            })
    
    # Generate data for each day and city
    for day_idx, date in enumerate(dates):
        month = date.month
        season_adj = SEASONAL_PATTERNS[month]
        
        for city in INDIAN_CITIES:
            # Check if there's an active event
            active_event = None
            for event in events[city["name"]]:
                if event["start"] <= day_idx < event["end"]:
                    active_event = event
                    break
            
            # Base climate values
            temp = city["temp_base"] + season_adj[0] + random.uniform(-2, 2)
            rain = max(0, city["rain_base"] + season_adj[1] + random.uniform(-10, 10))
            humidity = max(20, min(95, city["humidity_base"] + season_adj[2] + random.uniform(-5, 5)))
            wind = max(0, city["wind_base"] + season_adj[3] + random.uniform(-3, 3))
            pm25 = max(10, city["pm25_base"] + season_adj[4] + random.uniform(-10, 10))
            
            # Apply event adjustments if active
            event_name = None
            if active_event:
                event_name = active_event["event"]
                temp += active_event["temp_adj"]
                rain = max(0, rain + active_event["rain_adj"])
                humidity = max(20, min(95, humidity + active_event["humidity_adj"]))
                wind = max(0, wind + active_event["wind_adj"])
                pm25 = max(10, pm25 + active_event["pm25_adj"])
            
            # Calculate health impacts
            health = calculate_health_impacts(temp, rain, humidity, wind, pm25, event_name, city["population"])
            
            # Create row
            row = {
                "date": date.strftime("%Y-%m-%d"),
                "city": city["name"],
                "temp": round(temp, 1),
                "rain": round(rain, 1),
                "humidity": round(humidity, 1),
                "wind": round(wind, 1),
                "pm25": round(pm25, 1),
                "event": event_name if event_name else "None",
                "population": city["population"]
            }
            
            # Add health impacts
            row.update(health)
            
            # Add high risk flags
            row["high_heat_risk"] = 1 if temp > 35 else 0
            row["high_flood_risk"] = 1 if rain > 100 else 0
            row["high_resp_risk"] = 1 if pm25 > 100 else 0
            row["high_vector_risk"] = 1 if (temp > 30 and humidity > 70) else 0
            row["high_waterborne_risk"] = 1 if rain > 80 else 0
            
            # Add to dataset
            all_data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Add some tips based on risks
    tips = []
    sustainability_tips = []
    
    for _, row in df.iterrows():
        # Health tips
        day_tips = []
        if row["temp"] > 35:
            day_tips.append("Stay hydrated and avoid outdoor activities during peak heat")
        if row["rain"] > 100:
            day_tips.append("Avoid flooded areas and boil drinking water")
        if row["pm25"] > 100:
            day_tips.append("Wear masks outdoors and use air purifiers indoors")
        if row["temp"] > 30 and row["humidity"] > 70:
            day_tips.append("Use mosquito repellents and eliminate standing water")
        
        # Add personalized tips for vulnerable groups
        if row["temp"] > 33:
            day_tips.append("ELDERLY: Stay in cool areas and drink water regularly")
            day_tips.append("CHILDREN: Limit outdoor play to early morning or evening")
        
        # Sustainability tips
        day_sustainability = []
        if row["temp"] > 35:
            day_sustainability.append("Use natural cooling methods before air conditioning")
        if row["rain"] > 80:
            day_sustainability.append("Harvest rainwater for non-drinking purposes")
        if row["pm25"] > 100:
            day_sustainability.append("Reduce generator use and switch to clean energy sources")
        
        tips.append("|".join(day_tips) if day_tips else "No special precautions needed")
        sustainability_tips.append("|".join(day_sustainability) if day_sustainability else "Standard practices apply")
    
    df["health_tips"] = tips
    df["sustainability_tips"] = sustainability_tips
    
    return df

def save_synthetic_data(df):
    """Save the synthetic data to CSV"""
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Synthetic data saved to {OUTPUT_FILE}")
    print(f"Generated {len(df)} records for {len(df['city'].unique())} cities")

if __name__ == "__main__":
    print("Generating synthetic climate and health data for India...")
    df = generate_synthetic_data()
    save_synthetic_data(df)
    print("Done!")
