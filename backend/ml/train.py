"""
ML model training for the Climate-Resilient Healthcare System
Trains multiple XGBoost models for risk prediction, disease forecasting, and capacity planning
"""
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import accuracy_score, r2_score, classification_report
import time

# Constants
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../local.db"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    """Load data from SQLite database and merge tables"""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return None, None, None, None
    
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # Load tables
    climate = pd.read_sql("SELECT * FROM climate", engine, parse_dates=["date"])
    health = pd.read_sql("SELECT * FROM health", engine, parse_dates=["date"])
    capacity = pd.read_sql("SELECT * FROM capacity", engine, parse_dates=["date"])
    risk = pd.read_sql("SELECT * FROM risk", engine, parse_dates=["date"])
    
    # Merge tables
    merged = climate.merge(health, on=["date", "city"])
    merged = merged.merge(capacity, on=["date", "city"])
    merged = merged.merge(risk, on=["date", "city"])
    
    print(f"Loaded {len(merged)} records from database")
    return merged, climate, health, capacity

def prepare_features_targets(data):
    """Prepare features and target variables for different models"""
    if data is None:
        return None
    
    # Features for all models
    features = data[['temp', 'rain', 'humidity', 'wind', 'pm25', 'lagged_temp']]
    
    # Add month as a feature (seasonal patterns)
    data['month'] = data['date'].dt.month
    features['month'] = data['date'].dt.month
    
    # Add one-hot encoding for cities
    city_dummies = pd.get_dummies(data['city'], prefix='city')
    features = pd.concat([features, city_dummies], axis=1)
    
    # Add event encoding
    event_dummies = pd.get_dummies(data['event'], prefix='event')
    features = pd.concat([features, event_dummies], axis=1)
    
    # Target variables for different models
    risk_targets = {
        'high_heat_risk': data['high_heat_risk'],
        'high_flood_risk': data['high_flood_risk'],
        'high_resp_risk': data['high_resp_risk'],
        'high_vector_risk': data['high_vector_risk'],
        'high_waterborne_risk': data['high_waterborne_risk']
    }
    
    disease_targets = {
        'heat_stress_cases': data['heat_stress_cases'],
        'flood_injuries': data['flood_injuries'],
        'resp_issues': data['resp_issues'],
        'vector_diseases': data['vector_diseases'],
        'waterborne_diseases': data['waterborne_diseases'],
        'mental_health_cases': data['mental_health_cases']
    }
    
    capacity_targets = {
        'beds_needed': data['beds_needed'],
        'staff_needed': data['staff_needed'],
        'icu_needed': data['icu_needed'],
        'ventilators_needed': data['ventilators_needed'],
        'ambulances_needed': data['ambulances_needed'],
        'economic_cost': data['economic_cost']
    }
    
    return features, risk_targets, disease_targets, capacity_targets

def train_risk_models(features, targets):
    """Train binary classification models for risk prediction"""
    if features is None or targets is None:
        return None
    
    models = {}
    results = {}
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Save scaler
    joblib.dump(scaler, os.path.join(MODELS_DIR, "risk_scaler.pkl"))
    
    for risk_type, y in targets.items():
        print(f"Training model for {risk_type}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save results
        results[risk_type] = {
            'accuracy': accuracy,
            'report': report
        }
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f"{risk_type}_model.pkl")
        joblib.dump(model, model_path)
        models[risk_type] = model
        
        print(f"  Accuracy: {accuracy:.4f}")
    
    return models, results

def train_disease_models(features, targets):
    """Train regression models for disease case prediction"""
    if features is None or targets is None:
        return None
    
    models = {}
    results = {}
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Save scaler
    joblib.dump(scaler, os.path.join(MODELS_DIR, "disease_scaler.pkl"))
    
    for disease_type, y in targets.items():
        print(f"Training model for {disease_type}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        
        # Save results
        results[disease_type] = {
            'r2_score': r2
        }
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f"{disease_type}_model.pkl")
        joblib.dump(model, model_path)
        models[disease_type] = model
        
        print(f"  R² Score: {r2:.4f}")
    
    return models, results

def train_capacity_models(features, targets):
    """Train regression models for capacity prediction"""
    if features is None or targets is None:
        return None
    
    models = {}
    results = {}
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Save scaler
    joblib.dump(scaler, os.path.join(MODELS_DIR, "capacity_scaler.pkl"))
    
    for capacity_type, y in targets.items():
        print(f"Training model for {capacity_type}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        
        # Save results
        results[capacity_type] = {
            'r2_score': r2
        }
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f"{capacity_type}_model.pkl")
        joblib.dump(model, model_path)
        models[capacity_type] = model
        
        print(f"  R² Score: {r2:.4f}")
    
    return models, results

def train_peak_time_model(data):
    """Analyze and identify peak times for different risks"""
    if data is None:
        return None
    
    # Group by month and calculate average risks
    monthly_risks = data.groupby(data['date'].dt.month).agg({
        'high_heat_risk': 'mean',
        'high_flood_risk': 'mean',
        'high_resp_risk': 'mean',
        'high_vector_risk': 'mean',
        'high_waterborne_risk': 'mean'
    })
    
    # Identify peak months for each risk
    peak_months = {
        'high_heat_risk': monthly_risks['high_heat_risk'].idxmax(),
        'high_flood_risk': monthly_risks['high_flood_risk'].idxmax(),
        'high_resp_risk': monthly_risks['high_resp_risk'].idxmax(),
        'high_vector_risk': monthly_risks['high_vector_risk'].idxmax(),
        'high_waterborne_risk': monthly_risks['high_waterborne_risk'].idxmax()
    }
    
    # Save peak time analysis
    peak_data = {
        'monthly_risks': monthly_risks.to_dict(),
        'peak_months': peak_months
    }
    
    joblib.dump(peak_data, os.path.join(MODELS_DIR, "peak_time_analysis.pkl"))
    
    # Print peak months
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    print("\nPeak Risk Months:")
    for risk, month in peak_months.items():
        print(f"  {risk}: {month_names[month]} (Month {month})")
    
    return peak_data

def run_training():
    """Run the complete model training pipeline"""
    print("Starting model training...")
    
    # Load data
    data, climate, health, capacity = load_data()
    if data is None:
        print("Failed to load data. Run ETL first.")
        return False
    
    # Prepare features and targets
    features, risk_targets, disease_targets, capacity_targets = prepare_features_targets(data)
    
    # Train models
    risk_models, risk_results = train_risk_models(features, risk_targets)
    disease_models, disease_results = train_disease_models(features, disease_targets)
    capacity_models, capacity_results = train_capacity_models(features, capacity_targets)
    
    # Analyze peak times
    peak_data = train_peak_time_model(data)
    
    # Save training metadata
    metadata = {
        'training_time': datetime.now().isoformat(),
        'data_size': len(data),
        'cities': data['city'].unique().tolist(),
        'risk_results': risk_results,
        'disease_results': disease_results,
        'capacity_results': capacity_results
    }
    
    joblib.dump(metadata, os.path.join(MODELS_DIR, "training_metadata.pkl"))
    
    print("\nTraining completed successfully!")
    print(f"Models saved to {MODELS_DIR}")
    return True

def continuous_training(interval=3600):
    """Run training in a continuous loop with specified interval (seconds)"""
    while True:
        print(f"\n[{datetime.now().isoformat()}] Running scheduled training...")
        run_training()
        print(f"Next training in {interval} seconds...")
        time.sleep(interval)

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    # Check if continuous mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = 3600  # Default: 1 hour
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                pass
        print(f"Starting continuous training with {interval} second interval...")
        continuous_training(interval)
    else:
        run_training()