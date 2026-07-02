"""Collect daily GTA 6 mention counts from Reddit and Hacker News.

No API keys required:
- Reddit: public JSON endpoints (needs a descriptive User-Agent)
- Hacker News: Algolia search API

Appends one row per source per day to data/mentions.csv.
Safe to re-run: today's rows are overwritten, not duplicated.
"""

import csv
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mentions.csv"
HEADERS = {"User-Agent": "gta6-marketing-teardown/1.0 (research project)"}
QUERIES = ['"GTA 6"', '"GTA VI"', '"Grand Theft Auto VI"']


def count_reddit_posts_last_24h() -> int:
    """Count Reddit posts mentioning GTA 6 in the last 24 hours (site-wide search)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    seen_ids = set()
    for query in QUERIES:
        after = None
        for _ in range(3):  # up to 300 posts per query
            params = {"q": query, "sort": "new", "limit": 100, "t": "day", "type": "link"}
            if after:
                params["after"] = after
            resp = requests.get(
                "https://www.reddit.com/search.json",
                params=params, headers=HEADERS, timeout=30,
            )
            resp.raise_for_status()
            children = resp.json().get("data", {}).get("children", [])
            if not children:
                break
            for post in children:
                d = post["data"]
                created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
                if created >= cutoff:
                    seen_ids.add(d["id"])
            after = resp.json()["data"].get("after")
            if not after:
                break
            time.sleep(2)  # be polite to the API
        time.sleep(2)
    return len(seen_ids)


def get_subreddit_subscribers(subreddit: str = "GTA6") -> int:
    resp = requests.get(
        f"https://www.reddit.com/r/{subreddit}/about.json",
        headers=HEADERS, timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["subscribers"]


def count_hn_mentions_last_24h() -> int:
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    total = 0
    for query in ["GTA 6", "GTA VI"]:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search_by_date",
            params={"query": query, "numericFilters": f"created_at_i>{cutoff_ts}", "hitsPerPage": 0},
            timeout=30,
        )
        resp.raise_for_status()
        total += resp.json()["nbHits"]
    return total


def upsert_rows(new_rows: list[dict]) -> None:
    fieldnames = ["date", "source", "metric", "value"]
    existing: list[dict] = []
    if DATA_PATH.exists():
        with open(DATA_PATH, newline="") as f:
            existing = list(csv.DictReader(f))
    today = new_rows[0]["date"]
    keep = [r for r in existing if not (r["date"] == today and any(
        r["source"] == n["source"] and r["metric"] == n["metric"] for n in new_rows))]
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(keep + new_rows)


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []

    try:
        rows.append({"date": today, "source": "reddit", "metric": "posts_24h",
                     "value": count_reddit_posts_last_24h()})
    except Exception as e:
        print(f"Reddit posts failed: {e}")

    try:
        rows.append({"date": today, "source": "reddit", "metric": "r_gta6_subscribers",
                     "value": get_subreddit_subscribers()})
    except Exception as e:
        print(f"Subscriber count failed: {e}")

    try:
        rows.append({"date": today, "source": "hackernews", "metric": "mentions_24h",
                     "value": count_hn_mentions_last_24h()})
    except Exception as e:
        print(f"HN mentions failed: {e}")

    if rows:
        upsert_rows(rows)
        print(f"Wrote {len(rows)} rows for {today}")
    else:
        raise SystemExit("All collectors failed")


if __name__ == "__main__":
    main()
