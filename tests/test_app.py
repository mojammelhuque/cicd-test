from app import build_location_query, summarize_forecast


def test_build_location_query_uses_city_and_country():
    query = build_location_query(country="UK", city="London", postcode="")
    assert query == "London,UK"


def test_build_location_query_uses_postcode_when_city_missing():
    query = build_location_query(country="DE", city="", postcode="10115")
    assert query == "10115,DE"


def test_summarize_forecast_keeps_7_day_max():
    payload = {
        "list": [
            {"dt": 1700000000, "main": {"temp": 10, "feels_like": 8, "temp_min": 10, "temp_max": 12}, "weather": [{"main": "Clouds", "description": "few clouds"}]},
            {"dt": 1700086400, "main": {"temp": 12, "feels_like": 10, "temp_min": 11, "temp_max": 14}, "weather": [{"main": "Clear", "description": "clear sky"}]},
            {"dt": 1700172800, "main": {"temp": 14, "feels_like": 11, "temp_min": 13, "temp_max": 15}, "weather": [{"main": "Rain", "description": "light rain"}]},
            {"dt": 1700259200, "main": {"temp": 11, "feels_like": 9, "temp_min": 9, "temp_max": 12}, "weather": [{"main": "Clouds", "description": "broken clouds"}]},
            {"dt": 1700345600, "main": {"temp": 16, "feels_like": 14, "temp_min": 15, "temp_max": 18}, "weather": [{"main": "Clear", "description": "clear sky"}]},
            {"dt": 1700432000, "main": {"temp": 9, "feels_like": 7, "temp_min": 7, "temp_max": 10}, "weather": [{"main": "Rain", "description": "moderate rain"}]},
            {"dt": 1700518400, "main": {"temp": 13, "feels_like": 12, "temp_min": 12, "temp_max": 14}, "weather": [{"main": "Clouds", "description": "scattered clouds"}]},
        ]
    }

    result = summarize_forecast(payload)

    assert len(result) == 7
    assert result[0]["temp_min"] == 10
    assert result[0]["temp_max"] == 12
