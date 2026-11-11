import argparse
import logging
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("taxi")

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
RAW_DIR = Path("data/raw/taxi")


def build_url(year: int, month: int) -> str:
    return f"{BASE_URL}/yellow_tripdata_{year}-{month:02d}.parquet"


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    tmp.replace(dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description="Ingest NYC yellow taxi trips for one month")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()

    url = build_url(args.year, args.month)
    dest = RAW_DIR / f"yellow_{args.year}-{args.month:02d}.parquet"
    log.info("Downloading %s", url)
    try:
        path = download(url, dest)
        size_mb = path.stat().st_size / 1_000_000
        log.info("Saved %.1f MB to %s", size_mb, path)
    except requests.RequestException as e:
        log.error("Download failed: %s", e)
        raise


if __name__ == "__main__":
    main()