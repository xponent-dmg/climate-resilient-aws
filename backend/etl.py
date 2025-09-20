"""
ETL process for the Climate-Resilient Healthcare System
Loads synthetic data, processes it, and stores in SQLite database
"""
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import synthetic_data_generator

# Constants
DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SYNTHETIC_DATA_PATH = os.path.join(DATA_DIR, "synthetic_climate_health_2023.csv")

# SQLAlchemy setup
Base = declarative_base()

class Climate(Base):
    __tablename__ = 'climate'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    temp = Column(Float)
    rain = Column(Float)
    humidity = Column(Float)
    wind = Column(Float)
    pm25 = Column(Float)
    event = Column(String)
    lagged_temp = Column(Float)  # 7-day lagged temperature
    
class Health(Base):
    __tablename__ = 'health'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    heat_stress_cases = Column(Float)
    flood_injuries = Column(Float)
    resp_issues = Column(Float)
    vector_diseases = Column(Float)
    waterborne_diseases = Column(Float)
    mental_health_cases = Column(Float)
    emergency_calls = Column(Float)
    
class Capacity(Base):
    __tablename__ = 'capacity'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    beds_needed = Column(Integer)
    staff_needed = Column(Integer)
    icu_needed = Column(Integer)
    ventilators_needed = Column(Integer)
    ambulances_needed = Column(Integer)
    economic_cost = Column(Integer)  # in thousands of rupees
    
class Risk(Base):
    __tablename__ = 'risk'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    high_heat_risk = Column(Boolean)
    high_flood_risk = Column(Boolean)
    high_resp_risk = Column(Boolean)
    high_vector_risk = Column(Boolean)
    high_waterborne_risk = Column(Boolean)
    
class Tips(Base):
    __tablename__ = 'tips'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    health_tips = Column(String)
    sustainability_tips = Column(String)

def ensure_synthetic_data():
    """Check if synthetic data exists, generate if not"""
    if not os.path.exists(SYNTHETIC_DATA_PATH):
        print("Synthetic data not found. Generating...")
        df = synthetic_data_generator.generate_synthetic_data()
        synthetic_data_generator.save_synthetic_data(df)
    else:
        print(f"Using existing synthetic data from {SYNTHETIC_DATA_PATH}")

def load_data():
    """Load synthetic climate and health data"""
    ensure_synthetic_data()
    df = pd.read_csv(SYNTHETIC_DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df

def process_data(df):
    """Process and clean the data"""
    # Add lagged temperature (7-day lag)
    df = df.sort_values(['city', 'date'])
    df['lagged_temp'] = df.groupby('city')['temp'].shift(7)
    
    # Fill missing values
    df = df.fillna({
        'lagged_temp': df['temp'],  # Use current temp if no lag available
        'event': 'None'
    })
    
    return df

def save_to_db(df):
    """Save processed data to SQLite database"""
    # Create SQLite engine
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Prepare dataframes for each table
    climate_df = df[['date', 'city', 'temp', 'rain', 'humidity', 'wind', 'pm25', 'event', 'lagged_temp']]
    
    health_df = df[['date', 'city', 'heat_stress_cases', 'flood_injuries', 'resp_issues', 
                    'vector_diseases', 'waterborne_diseases', 'mental_health_cases', 'emergency_calls']]
    
    capacity_df = df[['date', 'city', 'beds_needed', 'staff_needed', 'icu_needed', 
                      'ventilators_needed', 'ambulances_needed', 'economic_cost']]
    
    risk_df = df[['date', 'city', 'high_heat_risk', 'high_flood_risk', 'high_resp_risk', 
                  'high_vector_risk', 'high_waterborne_risk']]
    
    tips_df = df[['date', 'city', 'health_tips', 'sustainability_tips']]
    
    # Save to database
    climate_df.to_sql('climate', engine, if_exists='replace', index=False)
    health_df.to_sql('health', engine, if_exists='replace', index=False)
    capacity_df.to_sql('capacity', engine, if_exists='replace', index=False)
    risk_df.to_sql('risk', engine, if_exists='replace', index=False)
    tips_df.to_sql('tips', engine, if_exists='replace', index=False)
    
    print(f"Data saved to {DB_PATH}")
    print(f"Processed {len(df)} records for {len(df['city'].unique())} cities")

def run_etl():
    """Run the full ETL process"""
    print("Starting ETL process...")
    df = load_data()
    processed_df = process_data(df)
    save_to_db(processed_df)
    print("ETL process completed successfully!")
    return True

if __name__ == "__main__":
    run_etl()