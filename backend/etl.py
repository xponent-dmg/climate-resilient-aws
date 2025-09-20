import os
import pandas as pd
from sqlalchemy import create_engine

RAW_FILE = os.path.join(os.path.dirname(__file__), "raw", "421820-2023.csv")
DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
REGION = "Delhi"


def run_etl():
    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"Raw CSV not found: {RAW_FILE}. Run ingest.py first.")

    print("Vibing through cleaning... loading CSV")
    df = pd.read_csv(RAW_FILE, parse_dates=["DATE"])  # expects DATE,TEMP,DEWP

    # Clean: drop nulls in TEMP/DEWP
    before = len(df)
    df = df.dropna(subset=["TEMP", "DEWP"]).copy()
    after = len(df)
    print(f"Vibing through cleaning... nulls dropped! {before - after} rows removed")

    # Feature engineering (mock additional climate vars)
    df["lagged_temp"] = df["TEMP"].shift(7)
    # Synthesize rain, wind, air pollution indices for demo
    # Simple cyclic or scaled transforms for deterministic mock values
    df = df.sort_values("DATE").reset_index(drop=True)
    df["RAIN"] = ((df.index % 5) * 2 + 1).astype(float)  # 1,3,5,7,9 pattern
    df["WIND"] = ((df.index % 7) + 2).astype(float)      # 2..8
    df["AIR"] = (50 + (df["DEWP"].rank(pct=True) * 150)).round(0)  # AQI-like 50..200
    df["region"] = REGION

    # Climate data
    climate = df[["DATE", "region", "TEMP", "DEWP", "RAIN", "WIND", "AIR", "lagged_temp"]].rename(
        columns={"TEMP": "temp", "DEWP": "humidity", "RAIN": "rain", "WIND": "wind", "AIR": "air"}
    )

    # Mock multi-risk health data (India-general demo)
    health = df[["DATE", "region", "TEMP", "RAIN", "AIR"]].copy()
    health["heat_cases"] = (health["TEMP"] * 0.3).round(2)
    health["flood_cases"] = (health["RAIN"] * 0.5).round(2)
    health["resp_cases"] = (health["AIR"] * 0.2 / 10).round(2)  # scale down AQI
    health["vector_cases"] = (health["TEMP"] * 0.1 + health["RAIN"] * 0.2).round(2)
    health = health[["DATE", "region", "heat_cases", "flood_cases", "resp_cases", "vector_cases"]]

    # Persist to SQLite
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.begin() as conn:
        climate.to_sql("climate", conn, if_exists="replace", index=False)
        health.to_sql("health", conn, if_exists="replace", index=False)
    print("ETL vibes: Multi-risks ready for prediction! ->", DB_PATH)


if __name__ == "__main__":
    run_etl()
