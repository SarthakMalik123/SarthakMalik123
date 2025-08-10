# SurakshitPath – Predict · Prevent · Prosper

A multilingual supply chain risk management dashboard built with Streamlit and scikit-learn.

## Features
- Login with email/password or Demo Mode
- Language switcher (English, हिन्दी)
- CSV upload, filters, and advanced toggles
- AI delay prediction (RandomForest)
- Folium route map with risky vendors and zones
- Optional real routing (OpenRouteService) and live weather (OpenWeatherMap)
- Reports and export to CSV/PDF
- Responsive, modern UI with custom theme

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add API keys if you have them
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Docker
```bash
docker build -t surakshitpath:latest .
docker run --env-file .env -p 8501:8501 surakshitpath:latest
```

## API Keys
- OpenRouteService (routing): create a free key at `https://openrouteservice.org` and set `ORS_API_KEY` in `.env`.
- OpenWeatherMap (weather): create a free key at `https://openweathermap.org/api` and set `OPENWEATHER_API_KEY` in `.env`.

Create `.env` from template:
```bash
cp .env.example .env
# edit .env
```

## Deploy (Streamlit Community Cloud)
- Push this repo to GitHub
- Create a new app on Streamlit Cloud pointing to `app.py`
- Set Python version to 3.11 and ensure `requirements.txt` is detected
- Add Secrets (from `.env`) under App settings → Secrets:
```
ORS_API_KEY="..."
OPENWEATHER_API_KEY="..."
```

## Deploy (Render/ Railway/ ECS)
- Build from Dockerfile
- Provide `.env` environment variables
- Expose port `8501`

## Environment
- Python 3.11+
- No external API keys required (routes simulated if keys absent)

## Data
Use `data/sample_vendors.csv` as a starter. Required columns:
```
vendor_id, vendor_name, state, product, risk_level, avg_delay_pct, lat, lon, distance_km, past_delays, weather_score
```

## Notes
- Authentication is demo-only (local JSON). For production, integrate a managed auth provider.
