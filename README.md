# Weather Forecast App

A simple Streamlit application that lets a user search for weather by country, city, or postcode and view the current conditions and a 7-day forecast.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Environment variables

Set `OPENWEATHER_API_KEY` with your weather API key.

## Deployment model

- `dev` branch: automatic CI validation
- `main` branch: production branch with manual approval before deployment
