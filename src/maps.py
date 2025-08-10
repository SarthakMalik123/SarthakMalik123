from __future__ import annotations
import folium
from folium.plugins import BeautifyIcon
import pandas as pd
from typing import Tuple, List, Dict

RISK_COLOR = {
    "Low": "blue",
    "Medium": "orange",
    "High": "red",
}


def create_map(df: pd.DataFrame, lang_popup: callable, show_zones: bool, source: Tuple[float, float] | None, dest: Tuple[float, float] | None) -> folium.Map:
    center = [df["lat"].mean() or 20.5937, df["lon"].mean() or 78.9629]
    m = folium.Map(location=center, zoom_start=5, tiles="cartodbpositron")

    # Risk markers
    for _, row in df.iterrows():
        risk = str(row.get("risk_level", "Medium"))
        color = RISK_COLOR.get(risk, "gray")
        popup_html = lang_popup(row)
        folium.Marker(
            location=[row.get("lat", 0), row.get("lon", 0)],
            popup=folium.Popup(popup_html, max_width=300),
            icon=BeautifyIcon(border_color=color, text_color=color, icon_shape='marker', number=str(int(row.get("avg_delay_pct", 0))))
        ).add_to(m)

    # Optional risk zones (mock polygon)
    if show_zones:
        folium.Rectangle(
            bounds=[[19.0, 72.5], [19.5, 73.5]],
            color="red",
            fill=True,
            fill_opacity=0.15,
            tooltip="High Risk Zone"
        ).add_to(m)

    # Simple straight-line route between source and destination if provided
    if source and dest:
        folium.PolyLine(locations=[source, dest], color="blue", weight=4, opacity=0.8, tooltip="Safe Route").add_to(m)
        folium.Marker(source, icon=folium.Icon(color="green", icon="play"), tooltip="Source").add_to(m)
        folium.Marker(dest, icon=folium.Icon(color="blue", icon="flag"), tooltip="Destination").add_to(m)

    return m