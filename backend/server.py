from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import pandas as pd
from sqlalchemy import create_engine
from fastapi.responses import PlainTextResponse

DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")
REGION = "Delhi"

app = FastAPI(title="CRHS Local API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,allow_headers=["*"]
)

class PredictRequest(BaseModel):
    region: str | None = None

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/predict")
async def predict(_: PredictRequest):
    if not os.path.exists(DB_PATH):
        return {"error": "DB not found. Run ETL."}
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        climate = pd.read_sql("SELECT DATE, temp FROM climate ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
        health = pd.read_sql("SELECT DATE, heat_cases FROM health ORDER BY DATE ASC", conn, parse_dates=["DATE"])  # noqa: E501
    avg_cases = health["heat_cases"].mean() if not health.empty else 0.0
    risk = min(1.0, max(0.0, float(avg_cases) / 15.0))
    temps_tail = climate.tail(2)["temp"].tolist() if not climate.empty else []
    resp = {"risk": round(risk, 2), "temps": temps_tail, "region": REGION}
    return resp

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
