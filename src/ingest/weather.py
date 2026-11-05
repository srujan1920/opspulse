import argparse
import calendar
import json
import logging
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("weather")

API_URL = "https://archive-api.open-meteo.com/v1/archive"
RAW_DIR = Path("data/raw/weather")


def month_range(year: int, month: int) -> tuple[str, str]:
    """Return ('2024-01-01', '2024-01-31') for year=2024, month=1."""
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date


def fetch_weather(start_date: str, end_date: str) -> dict:
    params = {
        "latitude": 40.71,
        "longitude": -74.01,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,precipitation",
        "timezone": "America/New_York",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw(data: dict, year: int, month: int) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{year}-{month:02d}.json"
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def main():
    parser = argparse.ArgumentParser(description="Ingest hourly NYC weather for one month")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()

    start, end = month_range(args.year, args.month)
    log.info("Fetching weather %s to %s", start, end)
    try:
        data = fetch_weather(start, end)
        path = save_raw(data, args.year, args.month)
        log.info("Saved %d rows to %s", len(data["hourly"]["time"]), path)
    except requests.RequestException as e:
        log.error("API request failed: %s", e)
        raise


if __name__ == "__main__":
    main()