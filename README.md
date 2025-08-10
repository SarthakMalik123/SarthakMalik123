# SurakshitPath – Predict · Prevent · Prosper

A multilingual supply chain risk management dashboard built with Streamlit and scikit-learn.

## Features
- Login with email/password or Demo Mode
- Language switcher (English, हिन्दी)
- CSV upload, filters, and advanced toggles
- AI delay prediction (RandomForest)
- Folium route map with risky vendors and zones
- Reports and export to CSV/PDF
- Responsive, modern UI with custom theme

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Docker
```bash
docker build -t surakshitpath:latest .
docker run -p 8501:8501 surakshitpath:latest
```

## Deploy (Streamlit Community Cloud)
- Push this repo to GitHub
- Create a new app on Streamlit Cloud pointing to `app.py`
- Set Python version to 3.11 and ensure `requirements.txt` is detected

## Environment
- Python 3.11+
- No external API keys required (routes simulated)

## Data
Use `data/sample_vendors.csv` as a starter. Required columns:
```
vendor_id, vendor_name, state, product, risk_level, avg_delay_pct, lat, lon, distance_km, past_delays, weather_score
```

## Notes
- Authentication here is for demo only (local JSON store). For production, integrate a proper auth provider.
