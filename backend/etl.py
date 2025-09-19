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

    # Feature engineering
    df["lagged_temp"] = df["TEMP"].shift(7)
    df["region"] = REGION

    # Climate data
    climate = df[["DATE", "region", "TEMP", "DEWP", "lagged_temp"]].rename(
        columns={"TEMP": "temp", "DEWP": "humidity"}
    )

    # Mock health data
    health = df[["DATE", "region", "TEMP"]].copy()
    health["heat_cases"] = (health["TEMP"] * 0.3).round(2)
    health = health.rename(columns={"TEMP": "temp"})[["DATE", "region", "heat_cases"]]

    # Persist to SQLite
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.begin() as conn:
        climate.to_sql("climate", conn, if_exists="replace", index=False)
        health.to_sql("health", conn, if_exists="replace", index=False)
    print("ETL vibes: Data cleaned and health mocked—ready for ML! ->", DB_PATH)


if __name__ == "__main__":
    run_etl()
