"""
FastAPI server for the Climate-Resilient Healthcare System
Provides endpoints for risk prediction, disease forecasting, capacity planning, and more
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import joblib
from datetime import datetime, timedelta
import json
import random

# Path constants
DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Create FastAPI app
app = FastAPI(
    title="Climate-Resilient Healthcare System API",
    description="API for climate-related health risk prediction and management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Pydantic models for request/response
class PredictRequest(BaseModel):
    city: str = "Delhi"
    date: Optional[str] = None  # If None, use latest data or today

class CapacityRequest(BaseModel):
    beds: int
    staff: int
    icu: Optional[int] = None
    ventilators: Optional[int] = None
    ambulances: Optional[int] = None

class FeedbackRequest(BaseModel):
    city: str
    incident_type: str
    description: str
    severity: int
    contact: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    city: Optional[str] = "Delhi"

# In-memory stores for demo
_capacity_store = {"beds": 50, "staff": 20, "icu": 5, "ventilators": 3, "ambulances": 2}
_feedback_store = []
_notes_store = []

# Helper functions
def get_db_connection():
    """Get SQLAlchemy engine for database connection"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found. Run ETL first.")
    return create_engine(f"sqlite:///{DB_PATH}")

def load_models():
    """Load trained ML models"""
    models = {}
    scalers = {}
    
    # Check if models directory exists
    if not os.path.exists(MODELS_DIR):
        return None, None
    
    # Try to load risk models
    try:
        risk_scaler_path = os.path.join(MODELS_DIR, "risk_scaler.pkl")
        if os.path.exists(risk_scaler_path):
            scalers["risk"] = joblib.load(risk_scaler_path)
            
            # Load individual risk models
            risk_types = ['high_heat_risk', 'high_flood_risk', 'high_resp_risk', 
                         'high_vector_risk', 'high_waterborne_risk']
            
            for risk_type in risk_types:
                model_path = os.path.join(MODELS_DIR, f"{risk_type}_model.pkl")
                if os.path.exists(model_path):
                    models[risk_type] = joblib.load(model_path)
    except Exception as e:
        print(f"Error loading risk models: {e}")
    
    # Try to load disease models
    try:
        disease_scaler_path = os.path.join(MODELS_DIR, "disease_scaler.pkl")
        if os.path.exists(disease_scaler_path):
            scalers["disease"] = joblib.load(disease_scaler_path)
            
            # Load individual disease models
            disease_types = ['heat_stress_cases', 'flood_injuries', 'resp_issues',
                            'vector_diseases', 'waterborne_diseases', 'mental_health_cases']
            
            for disease_type in disease_types:
                model_path = os.path.join(MODELS_DIR, f"{disease_type}_model.pkl")
                if os.path.exists(model_path):
                    models[disease_type] = joblib.load(model_path)
    except Exception as e:
        print(f"Error loading disease models: {e}")
    
    # Try to load capacity models
    try:
        capacity_scaler_path = os.path.join(MODELS_DIR, "capacity_scaler.pkl")
        if os.path.exists(capacity_scaler_path):
            scalers["capacity"] = joblib.load(capacity_scaler_path)
            
            # Load individual capacity models
            capacity_types = ['beds_needed', 'staff_needed', 'icu_needed',
                             'ventilators_needed', 'ambulances_needed', 'economic_cost']
            
            for capacity_type in capacity_types:
                model_path = os.path.join(MODELS_DIR, f"{capacity_type}_model.pkl")
                if os.path.exists(model_path):
                    models[capacity_type] = joblib.load(model_path)
    except Exception as e:
        print(f"Error loading capacity models: {e}")
    
    # Try to load peak time analysis
    try:
        peak_path = os.path.join(MODELS_DIR, "peak_time_analysis.pkl")
        if os.path.exists(peak_path):
            models["peak_time"] = joblib.load(peak_path)
    except Exception as e:
        print(f"Error loading peak time analysis: {e}")
    
    return models, scalers

def get_latest_data(city, engine):
    """Get the latest climate data for a city"""
    query = f"""
    SELECT c.*, r.high_heat_risk, r.high_flood_risk, r.high_resp_risk, 
           r.high_vector_risk, r.high_waterborne_risk
    FROM climate c
    JOIN risk r ON c.date = r.date AND c.city = r.city
    WHERE c.city = '{city}'
    ORDER BY c.date DESC
    LIMIT 1
    """
    
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for city: {city}")
        return df.iloc[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_city_data(city, days=7, engine=None):
    """Get recent climate and health data for a city"""
    if engine is None:
        engine = get_db_connection()
    
    query = f"""
    SELECT c.date, c.temp, c.rain, c.humidity, c.wind, c.pm25, c.event,
           h.heat_stress_cases, h.flood_injuries, h.resp_issues, 
           h.vector_diseases, h.waterborne_diseases, h.mental_health_cases,
           r.high_heat_risk, r.high_flood_risk, r.high_resp_risk, 
           r.high_vector_risk, r.high_waterborne_risk,
           cap.beds_needed, cap.staff_needed, cap.icu_needed,
           cap.ventilators_needed, cap.ambulances_needed, cap.economic_cost,
           t.health_tips, t.sustainability_tips
    FROM climate c
    JOIN health h ON c.date = h.date AND c.city = h.city
    JOIN risk r ON c.date = r.date AND c.city = r.city
    JOIN capacity cap ON c.date = cap.date AND c.city = cap.city
    JOIN tips t ON c.date = t.date AND c.city = t.city
    WHERE c.city = '{city}'
    ORDER BY c.date DESC
    LIMIT {days}
    """
    
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for city: {city}")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def prepare_features(data, include_city=True, include_event=True):
    """Prepare features for model prediction"""
    # Base features
    features = data[['temp', 'rain', 'humidity', 'wind', 'pm25', 'lagged_temp']].copy()
    
    # Add month
    if isinstance(data['date'], pd.Timestamp):
        features['month'] = data['date'].month
    else:
        features['month'] = pd.to_datetime(data['date']).month
    
    # One-hot encoding for city (if we have multiple cities in the model)
    if include_city and 'city' in data:
        city_name = data['city']
        features[f'city_{city_name}'] = 1
    
    # One-hot encoding for event
    if include_event and 'event' in data:
        event_name = data['event']
        if event_name != 'None':
            features[f'event_{event_name}'] = 1
    
    return features

def get_chatbot_response(query, city):
    """Generate a response for the AI chatbot"""
    # Simple keyword-based responses
    query = query.lower()
    
    if "heat" in query or "hot" in query:
        return {
            "response": "During heat waves, stay hydrated, avoid outdoor activities during peak hours, and use cooling measures like fans or wet towels. The elderly and children are particularly vulnerable.",
            "related_risks": ["heat_stress", "dehydration"],
            "emergency_contact": "108 for ambulance"
        }
    
    elif "flood" in query or "rain" in query or "water" in query:
        return {
            "response": "In flood-prone areas, move to higher ground, avoid walking or driving through floodwater, and boil water before drinking. Watch for waterborne diseases like diarrhea and cholera.",
            "related_risks": ["drowning", "waterborne_diseases", "injuries"],
            "emergency_contact": "1078 for disaster management"
        }
    
    elif "breath" in query or "air" in query or "pollution" in query:
        return {
            "response": "During high air pollution, wear masks outdoors, use air purifiers indoors, and limit outdoor activities. People with asthma or respiratory conditions should keep medications handy.",
            "related_risks": ["respiratory_issues", "asthma_attacks"],
            "emergency_contact": "108 for medical emergencies"
        }
    
    elif "mosquito" in query or "dengue" in query or "malaria" in query:
        return {
            "response": "To prevent vector-borne diseases, use mosquito repellents, wear long sleeves and pants, and eliminate standing water. Watch for symptoms like fever, headache, and joint pain.",
            "related_risks": ["dengue", "malaria", "chikungunya"],
            "emergency_contact": "104 for health helpline"
        }
    
    elif "hospital" in query or "doctor" in query or "medical" in query:
        return {
            "response": f"For medical emergencies in {city}, call 108 for an ambulance. For non-emergency healthcare advice, call the national health helpline at 104.",
            "related_risks": ["all_medical_conditions"],
            "emergency_contact": "108 for ambulance, 104 for health helpline"
        }
    
    elif "mental" in query or "stress" in query or "anxiety" in query:
        return {
            "response": "During climate disasters, it's normal to feel stressed or anxious. Practice deep breathing, maintain routines, and reach out to loved ones. Professional help is available through mental health helplines.",
            "related_risks": ["anxiety", "depression", "post_traumatic_stress"],
            "emergency_contact": "1800-599-0019 for mental health helpline"
        }
    
    else:
        return {
            "response": f"I'm your Climate-Resilient Healthcare assistant. You can ask me about heat waves, floods, air pollution, vector-borne diseases, or how to access medical help in {city}.",
            "related_risks": [],
            "emergency_contact": "108 for emergencies, 104 for health helpline"
        }

# API Endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/predict")
async def predict(req: PredictRequest):
    """Predict climate-related health risks and impacts"""
    engine = get_db_connection()
    
    # Get latest data for the city
    latest_data = get_latest_data(req.city, engine)
    
    # Get recent data for trends
    recent_data = get_city_data(req.city, days=7, engine=engine)
    
    # Load models if available
    models, scalers = load_models()
    
    # Prepare response
    response = {
        "city": req.city,
        "date": latest_data["date"],
        "current_conditions": {
            "temp": float(latest_data["temp"]),
            "rain": float(latest_data["rain"]),
            "humidity": float(latest_data["humidity"]),
            "wind": float(latest_data["wind"]),
            "pm25": float(latest_data["pm25"]),
            "event": latest_data["event"]
        },
        "risks": {
            "heat": float(latest_data["high_heat_risk"]),
            "flood": float(latest_data["high_flood_risk"]),
            "resp": float(latest_data["high_resp_risk"]),
            "vector": float(latest_data["high_vector_risk"]),
            "waterborne": float(latest_data["high_waterborne_risk"])
        },
        "trends": {
            "temp": recent_data["temp"].tolist(),
            "rain": recent_data["rain"].tolist(),
            "dates": recent_data["date"].dt.strftime("%Y-%m-%d").tolist()
        }
    }
    
    # Add ML predictions if models are available
    if models and scalers:
        try:
            # Prepare features
            features = prepare_features(latest_data)
            features_df = pd.DataFrame([features])
            
            # Risk predictions
            if "risk" in scalers:
                X_scaled = scalers["risk"].transform(features_df)
                ml_risks = {}
                
                for risk_type, model in models.items():
                    if risk_type.startswith("high_") and risk_type.endswith("_risk"):
                        if hasattr(model, "predict_proba"):
                            prob = model.predict_proba(X_scaled)[0][1]
                            ml_risks[risk_type] = float(prob)
                        else:
                            pred = model.predict(X_scaled)[0]
                            ml_risks[risk_type] = float(pred)
                
                response["ml_risks"] = ml_risks
            
            # Disease predictions
            if "disease" in scalers:
                X_scaled = scalers["disease"].transform(features_df)
                ml_diseases = {}
                
                for disease_type, model in models.items():
                    if disease_type.endswith("_cases") or disease_type.endswith("_diseases"):
                        pred = model.predict(X_scaled)[0]
                        ml_diseases[disease_type] = float(pred)
                
                response["ml_diseases"] = ml_diseases
            
            # Capacity predictions
            if "capacity" in scalers:
                X_scaled = scalers["capacity"].transform(features_df)
                ml_capacity = {}
                
                for capacity_type, model in models.items():
                    if capacity_type.endswith("_needed") or capacity_type == "economic_cost":
                        pred = model.predict(X_scaled)[0]
                        ml_capacity[capacity_type] = int(pred)
                
                response["ml_capacity"] = ml_capacity
            
            # Peak time information
            if "peak_time" in models:
                peak_data = models["peak_time"]
                current_month = datetime.now().month
                
                # Convert month numbers to names
                month_names = {
                    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
                }
                
                peak_info = {}
                for risk_type, peak_month in peak_data["peak_months"].items():
                    months_away = (peak_month - current_month) % 12
                    status = "current" if months_away == 0 else "upcoming" if months_away <= 3 else "distant"
                    
                    peak_info[risk_type] = {
                        "peak_month": month_names[peak_month],
                        "months_away": months_away,
                        "status": status
                    }
                
                response["peak_times"] = peak_info
        
        except Exception as e:
            response["ml_error"] = str(e)
    
    # Get health tips
    try:
        tips_query = f"""
        SELECT health_tips, sustainability_tips
        FROM tips
        WHERE city = '{req.city}'
        ORDER BY date DESC
        LIMIT 1
        """
        tips_df = pd.read_sql(tips_query, engine)
        if not tips_df.empty:
            response["tips"] = {
                "health": tips_df.iloc[0]["health_tips"].split("|"),
                "sustainability": tips_df.iloc[0]["sustainability_tips"].split("|")
            }
    except Exception:
        pass
    
    return response

@app.get("/capacity")
async def get_capacity():
    """Get current capacity settings"""
    return _capacity_store

@app.post("/capacity")
async def set_capacity(cap: CapacityRequest):
    """Update capacity settings"""
    _capacity_store.update({
        "beds": cap.beds,
        "staff": cap.staff
    })
    
    if cap.icu is not None:
        _capacity_store["icu"] = cap.icu
    
    if cap.ventilators is not None:
        _capacity_store["ventilators"] = cap.ventilators
    
    if cap.ambulances is not None:
        _capacity_store["ambulances"] = cap.ambulances
    
    return {"status": "updated", **_capacity_store}

@app.get("/cities")
async def get_cities():
    """Get list of available cities"""
    engine = get_db_connection()
    
    try:
        query = "SELECT DISTINCT city FROM climate"
        df = pd.read_sql(query, engine)
        return {"cities": df["city"].tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit community feedback or incident report"""
    feedback_data = feedback.dict()
    feedback_data["timestamp"] = datetime.now().isoformat()
    feedback_data["id"] = len(_feedback_store) + 1
    
    _feedback_store.append(feedback_data)
    
    return {"status": "received", "id": feedback_data["id"]}

@app.get("/feedback")
async def get_feedback():
    """Get all community feedback"""
    return {"feedback": _feedback_store}

@app.post("/notes")
async def add_note(city: str, note: str):
    """Add a team note"""
    note_data = {
        "id": len(_notes_store) + 1,
        "city": city,
        "note": note,
        "timestamp": datetime.now().isoformat(),
        "user": "Admin"  # In a real system, this would come from authentication
    }
    
    _notes_store.append(note_data)
    
    return {"status": "added", "id": note_data["id"]}

@app.get("/notes")
async def get_notes(city: Optional[str] = None):
    """Get team notes, optionally filtered by city"""
    if city:
        filtered_notes = [note for note in _notes_store if note["city"] == city]
        return {"notes": filtered_notes}
    return {"notes": _notes_store}

@app.post("/chat")
async def chat(req: ChatRequest):
    """AI chatbot for health guidance"""
    return get_chatbot_response(req.query, req.city)

@app.get("/reports/{city}")
async def get_report(city: str):
    """Generate a CSV report for a city"""
    engine = get_db_connection()
    
    try:
        # Get data for the city
        df = get_city_data(city, days=30, engine=engine)
        
        # Convert to CSV format
        csv_data = df.to_csv(index=False)
        
        # In a real system, we would return this as a downloadable file
        # For now, we'll just return the CSV content
        return {"csv_data": csv_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/emergency-contacts/{city}")
async def get_emergency_contacts(city: str):
    """Get emergency contacts for a city"""
    # In a real system, this would come from a database
    # For now, we'll return mock data
    contacts = {
        "Delhi": {
            "ambulance": "102",
            "fire": "101",
            "police": "100",
            "disaster_management": "1078",
            "hospitals": [
                {"name": "AIIMS Delhi", "phone": "011-26588500"},
                {"name": "Safdarjung Hospital", "phone": "011-26707444"}
            ]
        },
        "Mumbai": {
            "ambulance": "108",
            "fire": "101",
            "police": "100",
            "disaster_management": "1916",
            "hospitals": [
                {"name": "KEM Hospital", "phone": "022-24136051"},
                {"name": "Lilavati Hospital", "phone": "022-26455891"}
            ]
        }
    }
    
    if city in contacts:
        return contacts[city]
    
    # Default contacts if city not found
    return {
        "ambulance": "108",
        "fire": "101",
        "police": "100",
        "disaster_management": "1078",
        "hospitals": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)