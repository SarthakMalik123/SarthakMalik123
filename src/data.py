from __future__ import annotations
import os
import pandas as pd
import numpy as np
from typing import Tuple, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DATA = os.path.join(BASE_DIR, "data", "sample_vendors.csv")

REQUIRED_COLUMNS = [
    "vendor_id", "vendor_name", "state", "product", "risk_level",
    "avg_delay_pct", "lat", "lon", "distance_km", "past_delays", "weather_score"
]


def load_dataset(csv_bytes: bytes | None) -> pd.DataFrame:
    if csv_bytes is None:
        df = pd.read_csv(SAMPLE_DATA)
    else:
        from io import BytesIO
        df = pd.read_csv(BytesIO(csv_bytes))
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            # best effort: add missing with defaults
            if col in {"lat", "lon", "avg_delay_pct", "distance_km", "past_delays", "weather_score"}:
                df[col] = 0
            else:
                df[col] = "Unknown"
    # sanitize types
    numeric_cols = ["avg_delay_pct", "lat", "lon", "distance_km", "past_delays", "weather_score"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["risk_level"] = df["risk_level"].fillna("Medium")
    return df


def apply_filters(
    df: pd.DataFrame,
    states: List[str] | None,
    products: List[str] | None,
    risks: List[str] | None,
) -> pd.DataFrame:
    filtered = df.copy()
    if states:
        filtered = filtered[filtered["state"].isin(states)]
    if products:
        filtered = filtered[filtered["product"].isin(products)]
    if risks:
        filtered = filtered[filtered["risk_level"].isin(risks)]
    return filtered


RISK_COLOR_MAP = {
    "Low": "#10B981",
    "Medium": "#F59E0B",
    "High": "#EF4444",
}


def style_risk_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    def highlight(row):
        color = RISK_COLOR_MAP.get(str(row.get("risk_level", "Medium")), "#374151")
        return [f"background-color: {color}20" for _ in row]
    return df.style.apply(highlight, axis=1).format({
        "avg_delay_pct": "{:.1f}%",
        "distance_km": "{:.0f}",
        "weather_score": "{:.0f}",
    })


def compute_kpis(df: pd.DataFrame) -> Tuple[int, float, int, float]:
    total_vendors = len(df)
    avg_risk_score = (
        df["risk_level"].map({"Low": 0.33, "Medium": 0.66, "High": 1.0}).fillna(0.5).mean()
    ) * 100
    high_risk = (df["risk_level"] == "High").sum()
    avg_delay = df["avg_delay_pct"].mean()
    return total_vendors, avg_risk_score, high_risk, avg_delay