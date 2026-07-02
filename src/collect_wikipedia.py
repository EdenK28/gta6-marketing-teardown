"""Collect daily Wikipedia pageviews for the Grand Theft Auto VI article.

The Wikimedia REST API provides clean daily history back to 2015 — the best
free long-run attention proxy available. Rewrites the full CSV each run.
No API key required.
"""

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "wikipedia_pageviews.csv"
ARTICLE = "Grand_Theft_Auto_VI"
START = "20221001"  # a year before Trailer 1, for a clean baseline
HEADERS = {"User-Agent": "gta6-marketing-teardown/1.0 (research project)"}


def main() -> None:
    end = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{ARTICLE}/daily/{START}/{end}"
    )
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    items = resp.json()["items"]

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "pageviews"])
        for item in items:
            date = datetime.strptime(item["timestamp"][:8], "%Y%m%d").strftime("%Y-%m-%d")
            writer.writerow([date, item["views"]])

    print(f"Wrote {len(items)} days of pageviews")


if __name__ == "__main__":
    main()
