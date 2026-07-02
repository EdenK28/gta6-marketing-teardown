"""Collect Google Trends search interest for GTA 6.

Uses pytrends (unofficial API — occasionally rate-limited; the daily cron
retries tomorrow, so a single failure is harmless). Rewrites the full CSV.
"""

from pathlib import Path

from pytrends.request import TrendReq

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "google_trends.csv"


def main() -> None:
    pytrends = TrendReq(hl="en-US", tz=0, retries=3, backoff_factor=2)
    pytrends.build_payload(["GTA 6"], timeframe="2022-10-01 2026-12-31")
    df = pytrends.interest_over_time()
    if df.empty:
        raise SystemExit("Google Trends returned no data (likely rate-limited)")
    df = df.drop(columns=["isPartial"], errors="ignore")
    df.index.name = "date"
    df = df.rename(columns={"GTA 6": "search_interest"})
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH)
    print(f"Wrote {len(df)} rows of search interest")


if __name__ == "__main__":
    main()
