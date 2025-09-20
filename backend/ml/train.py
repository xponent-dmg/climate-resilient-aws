import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../local.db"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))


def load_dataset():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        climate = pd.read_sql(
            "SELECT DATE, temp, humidity, rain, wind, air, lagged_temp FROM climate ORDER BY DATE ASC",
            conn, parse_dates=["DATE"]
        )
        health = pd.read_sql(
            "SELECT DATE, heat_cases, flood_cases, resp_cases, vector_cases FROM health ORDER BY DATE ASC",
            conn, parse_dates=["DATE"]
        )
    df = climate.merge(health, on="DATE", how="inner").fillna(0)
    return df


def build_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["high_heat"] = (df["heat_cases"] > 10).astype(int)
    df["high_flood"] = (df["flood_cases"] > 8).astype(int)
    df["high_resp"] = (df["resp_cases"] > 6).astype(int)
    df["high_vector"] = (df["vector_cases"] > 5).astype(int)
    # Derived labels from climate
    df["high_drought"] = ((df["rain"] < 3) & (df["temp"] > 33)).astype(int)
    df["high_storm"] = ((df["wind"] > 6) & (df["rain"] > 5)).astype(int)
    df["high_air"] = (df["air"] > 150).astype(int)
    return df


FEATURES = ["temp", "humidity", "rain", "wind", "air", "lagged_temp"]
LABELS = [
    "high_heat",
    "high_flood",
    "high_resp",
    "high_vector",
    "high_drought",
    "high_storm",
    "high_air",
]


def train_models():
    Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    if df.empty:
        print("No data for training")
        return {}
    df = build_labels(df)
    X = df[FEATURES]
    results = {}
    for label in LABELS:
        y = df[label]
        if y.nunique() < 2:
            print(f"Skipping {label}: not enough class variety")
            continue
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        out_path = os.path.join(MODELS_DIR, f"{label}_xgb.pkl")
        joblib.dump(model, out_path)
        results[label] = {"accuracy": round(float(acc), 3), "model_path": out_path}
        print(f"Trained {label}: acc={acc:.3f}, saved to {out_path}")
    print("Predictions vibing for all disasters! (models trained)")
    return results


if __name__ == "__main__":
    train_models()
