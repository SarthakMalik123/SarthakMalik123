from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

FEATURE_COLUMNS = ["distance_km", "past_delays", "weather_score"]
TARGET_COLUMN = "avg_delay_pct"

@dataclass
class ModelResult:
    model: RandomForestRegressor
    r2: float
    mae: float


def train_model(df: pd.DataFrame) -> ModelResult:
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    return ModelResult(model=model, r2=r2, mae=mae)


def predict_delay(model: RandomForestRegressor, distance_km: float, past_delays: float, weather_score: float) -> float:
    X = np.array([[distance_km, past_delays, weather_score]])
    pred = float(model.predict(X)[0])
    return max(0.0, pred)


def add_predictions(df: pd.DataFrame, model: RandomForestRegressor) -> pd.DataFrame:
    df = df.copy()
    df["predicted_delay_pct"] = model.predict(df[FEATURE_COLUMNS])
    return df