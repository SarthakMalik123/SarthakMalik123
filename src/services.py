from __future__ import annotations
import requests
from typing import List, Tuple, Dict, Any

ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_route_openrouteservice(source: Tuple[float, float], dest: Tuple[float, float], api_key: str) -> Dict[str, Any]:
    # ORS expects [lon, lat]
    payload = {
        "coordinates": [
            [float(source[1]), float(source[0])],
            [float(dest[1]), float(dest[0])],
        ]
    }
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    r = requests.post(ORS_URL, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    feature = data["features"][0]
    coords_lonlat = feature["geometry"]["coordinates"]
    # Convert to [lat, lon]
    coords_latlon = [(c[1], c[0]) for c in coords_lonlat]
    summary = feature["properties"]["summary"]
    distance_km = float(summary.get("distance", 0)) / 1000.0
    duration_min = float(summary.get("duration", 0)) / 60.0
    return {
        "coords": coords_latlon,
        "distance_km": distance_km,
        "duration_min": duration_min,
    }


def get_weather_openweather(lat: float, lon: float, api_key: str) -> Dict[str, Any]:
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    r = requests.get(OWM_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    desc = data.get("weather", [{}])[0].get("description", "").title()
    temp = data.get("main", {}).get("temp")
    wind = data.get("wind", {}).get("speed")
    humidity = data.get("main", {}).get("humidity")
    return {
        "description": desc,
        "temp_c": temp,
        "wind_ms": wind,
        "humidity": humidity,
        "raw": data,
    }