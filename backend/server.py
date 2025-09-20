from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import pandas as pd
from sqlalchemy import create_engine
from fastapi.responses import PlainTextResponse, JSONResponse
import joblib
import numpy as np
from ml.capacity_model import predict_capacity, train_capacity_model

DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
REGION = "Delhi"

app = FastAPI(title="CRHS Local API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class PredictRequest(BaseModel):
    region: str | None = None

class Capacity(BaseModel):
    beds: int
    staff: int

class CapacityPredictRequest(BaseModel):
    so2: float = 10.0
    no2: float = 20.0
    pm10: float = 60.0
    pm25: float = 30.0
    region: str = "Delhi"
    season: str = "winter"

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/predict")
async def predict(_: PredictRequest):
    if not os.path.exists(DB_PATH):
        return {"error": "DB not found. Run ETL."}
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        climate = pd.read_sql("SELECT DATE, temp, humidity, rain, wind, air, lagged_temp FROM climate ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
        health = pd.read_sql("SELECT DATE, heat_cases, flood_cases, resp_cases, vector_cases FROM health ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
    def score(col, div):
        val = float(health[col].mean()) if not health.empty else 0.0
        return round(min(1.0, max(0.0, val / div)), 2)
    risks = {
        "heat": score("heat_cases", 15.0),
        "flood": score("flood_cases", 10.0),
        "resp": score("resp_cases", 8.0),
        "vector": score("vector_cases", 8.0),
    }
    temps_tail = climate.tail(2)["temp"].tolist() if not climate.empty else []

    # Optional ML predictions if models are trained
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    ml = {}
    if not climate.empty and os.path.isdir(models_dir):
        x_cols = ["temp", "humidity", "rain", "wind", "air", "lagged_temp"]
        X_last = climate.tail(1)[x_cols].fillna(0).to_numpy(dtype=float)
        labels = [
            "high_heat",
            "high_flood",
            "high_resp",
            "high_vector",
            "high_drought",
            "high_storm",
            "high_air",
        ]
        for label in labels:
            path = os.path.join(models_dir, f"{label}_xgb.pkl")
            if os.path.exists(path):
                try:
                    model = joblib.load(path)
                    proba = getattr(model, "predict_proba", None)
                    if callable(proba):
                        p = float(model.predict_proba(X_last)[0][1])
                    else:
                        p = float(model.predict(X_last)[0])
                    ml[label] = round(p, 3)
                except Exception:
                    continue

    return {"risks": risks, "temps": temps_tail, "region": REGION, "ml": ml}

_capacity_store = {"beds": 50, "staff": 20}

@app.get("/capacity")
async def get_capacity():
    return _capacity_store

@app.post("/capacity")
async def set_capacity(cap: Capacity):
    _capacity_store.update({"beds": int(cap.beds), "staff": int(cap.staff)})
    return {"ok": True, **_capacity_store}

@app.post("/capacity/predict")
async def predict_capacity_endpoint(req: CapacityPredictRequest):
    """Predict capacity needs based on environmental factors"""
    result = predict_capacity(
        so2=req.so2,
        no2=req.no2,
        pm10=req.pm10,
        pm25=req.pm25,
        region=req.region,
        season=req.season
    )
    return result

@app.post("/capacity/train")
async def train_capacity_endpoint():
    """Train capacity models using airquality data"""
    try:
        result = train_capacity_model()
        if result:
            return {"success": True, "metrics": result}
        return {"success": False, "error": "Training failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/reports", response_class=PlainTextResponse)
async def reports():
    if not os.path.exists(DB_PATH):
        return PlainTextResponse("date,region,risk\n", media_type="text/csv")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        health = pd.read_sql("SELECT DATE, heat_cases FROM health ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
    if health.empty:
        return PlainTextResponse("date,region,risk\n", media_type="text/csv")
    avg_cases = health["heat_cases"].mean()
    risk = min(1.0, max(0.0, float(avg_cases) / 15.0))
    last_date = health["DATE"].max().date()
    csv = f"date,region,risk\n{last_date},{REGION},{round(risk,2)}\n"
    return PlainTextResponse(csv, media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)