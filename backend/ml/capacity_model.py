"""
Capacity prediction model based on air quality and climate data
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# Model paths
BEDS_MODEL_PATH = os.path.join(MODELS_DIR, "capacity_beds.pkl")
STAFF_MODEL_PATH = os.path.join(MODELS_DIR, "capacity_staff.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "capacity_scaler.pkl")

# Season mapping
SEASON_MAPPING = {
    "winter": [0, 1],  # Jan-Feb
    "summer": [2, 3, 4],  # Mar-May
    "monsoon": [5, 6, 7, 8],  # Jun-Sep
    "autumn": [9, 10, 11]  # Oct-Dec
}

# Region risk mapping (based on air quality data)
def get_region_risk(region):
    """Get region risk factor based on historical air quality"""
    # Default medium risk
    if not region or region == "":
        return 0.5
    
    # High risk regions based on air quality data
    high_risk = ["Delhi", "Kolkata", "Mumbai", "Kanpur", "Lucknow", "Patna"]
    if region in high_risk:
        return 0.8
    
    # Medium risk regions
    medium_risk = ["Chennai", "Bangalore", "Hyderabad", "Ahmedabad", "Pune"]
    if region in medium_risk:
        return 0.5
    
    # Low risk for others
    return 0.3


def load_airquality_data():
    """Load and preprocess air quality data"""
    aq_file = os.path.join(DATA_DIR, "airquality.csv")
    if not os.path.exists(aq_file):
        print(f"Air quality data not found: {aq_file}")
        return None
    
    try:
        df = pd.read_csv(aq_file)
        # Clean up column names
        df.columns = [c.strip() for c in df.columns]
        
        # Handle missing values
        for col in ['SO2 Annual Average', 'NO2 Annual Average', 'PM10 Annual Average', 'PM2.5 Annual Average']:
            df[col] = pd.to_numeric(df[col].replace(['NM', '-'], np.nan), errors='coerce')
        
        # Create synthetic capacity data based on air quality
        # Higher pollution = higher capacity needs
        df['beds_capacity'] = 50 + df['PM2.5 Annual Average'].fillna(df['PM10 Annual Average']/2).fillna(30) * 0.8
        df['staff_capacity'] = 20 + df['PM2.5 Annual Average'].fillna(df['PM10 Annual Average']/2).fillna(30) * 0.3
        
        # Create features
        df['region_risk'] = df['State/Union Territory'].apply(get_region_risk)
        
        return df
    except Exception as e:
        print(f"Error loading air quality data: {e}")
        return None


def train_capacity_model():
    """Train capacity prediction models using air quality data"""
    df = load_airquality_data()
    if df is None:
        return None
    
    # Prepare features and targets
    features = ['SO2 Annual Average', 'NO2 Annual Average', 'PM10 Annual Average', 'PM2.5 Annual Average', 'region_risk']
    X = df[features].fillna(df[features].mean())
    y_beds = df['beds_capacity']
    y_staff = df['staff_capacity']
    
    # Split data
    X_train, X_test, y_beds_train, y_beds_test = train_test_split(X, y_beds, test_size=0.2, random_state=42)
    _, _, y_staff_train, y_staff_test = train_test_split(X, y_staff, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train beds model
    beds_model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    beds_model.fit(X_train_scaled, y_beds_train)
    beds_score = beds_model.score(X_test_scaled, y_beds_test)
    
    # Train staff model
    staff_model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    staff_model.fit(X_train_scaled, y_staff_train)
    staff_score = staff_model.score(X_test_scaled, y_staff_test)
    
    # Save models
    joblib.dump(beds_model, BEDS_MODEL_PATH)
    joblib.dump(staff_model, STAFF_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    return {
        "beds_r2": round(beds_score, 3),
        "staff_r2": round(staff_score, 3),
        "models_saved": [BEDS_MODEL_PATH, STAFF_MODEL_PATH]
    }


def predict_capacity(so2=10.0, no2=20.0, pm10=60.0, pm25=30.0, region="Delhi", season="winter"):
    """Predict capacity needs based on air quality and other factors"""
    # Check if models exist
    if not (os.path.exists(BEDS_MODEL_PATH) and os.path.exists(STAFF_MODEL_PATH) and os.path.exists(SCALER_PATH)):
        # Fall back to simple rule-based prediction
        region_factor = get_region_risk(region)
        season_factor = 1.2 if season == "monsoon" else 1.0
        pm_factor = min(1.5, max(0.5, pm25 / 30))
        
        beds = round(50 * region_factor * season_factor * pm_factor)
        staff = round(20 * region_factor * season_factor * pm_factor)
        
        return {
            "beds": beds,
            "staff": staff,
            "method": "rule-based",
            "factors": {
                "region": region_factor,
                "season": season_factor,
                "pollution": pm_factor
            }
        }
    
    try:
        # Load models
        beds_model = joblib.load(BEDS_MODEL_PATH)
        staff_model = joblib.load(STAFF_MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        # Prepare features
        region_risk = get_region_risk(region)
        features = np.array([[so2, no2, pm10, pm25, region_risk]])
        features_scaled = scaler.transform(features)
        
        # Predict
        beds = round(float(beds_model.predict(features_scaled)[0]))
        staff = round(float(staff_model.predict(features_scaled)[0]))
        
        # Apply seasonal adjustment
        season_factor = 1.2 if season == "monsoon" else 1.0 if season == "summer" else 0.9
        beds = round(beds * season_factor)
        staff = round(staff * season_factor)
        
        return {
            "beds": beds,
            "staff": staff,
            "method": "model-based",
            "factors": {
                "region": region_risk,
                "season": season_factor,
                "so2": so2,
                "no2": no2,
                "pm10": pm10,
                "pm25": pm25
            }
        }
    except Exception as e:
        print(f"Error predicting capacity: {e}")
        # Fall back to simple prediction
        return {
            "beds": 50,
            "staff": 20,
            "method": "fallback",
            "error": str(e)
        }


if __name__ == "__main__":
    # Train and test
    result = train_capacity_model()
    print(f"Training results: {result}")
    
    # Test prediction
    pred = predict_capacity(so2=15, no2=25, pm10=80, pm25=40, region="Delhi", season="monsoon")
    print(f"Prediction: {pred}")
