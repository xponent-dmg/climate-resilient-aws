import os
import json
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
REGION = "Delhi"


def compute_risk(df_health: pd.DataFrame) -> float:
    if df_health.empty:
        return 0.0
    avg_cases = df_health["heat_cases"].mean()
    # Scale to 0-1 roughly: assume > 10 cases is high risk
    risk = min(1.0, max(0.0, avg_cases / 15.0))
    return round(float(risk), 2)


def handler(event=None, context=None):
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found. Run ETL first.")

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        climate = pd.read_sql("SELECT DATE, region, temp, humidity, lagged_temp FROM climate ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
        health = pd.read_sql("SELECT DATE, region, heat_cases FROM health ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501

    risk = compute_risk(health)
    if risk > 0.7:
        print("Alert: High heat risk in Delhi!")

    temps = climate.tail(2)[["DATE", "temp"]]
    temps_list = [
        {"label": f"Day {i+1}", "value": float(v)}
        for i, v in enumerate(temps["temp"].tolist())
    ]

    resp = {
        "risk": risk,
        "temps": temps_list,
        "region": REGION,
    }
    print("API call complete—risk assessed!")
    # Simulate Lambda proxy
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(resp),
    }


if __name__ == "__main__":
    print(handler())
