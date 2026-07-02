# GTA 6: A Marketing Teardown in Data 🎮📊

**Rockstar Games is running one of the most efficient marketing campaigns in entertainment history — two trailers in 2.5 years, almost zero visible paid media, and record-breaking earned reach. This project measures it.**

I spent 6+ years running mobile user acquisition campaigns (Apple Search Ads, Google UAC, Meta, TikTok). This repo applies that lens — incrementality, attention decay, demand curves — to the biggest game launch ever, ahead of GTA 6's release on **November 19, 2026**.

🔴 **[Live Mentions Dashboard →](https://YOUR-APP.streamlit.app)** *(updates daily via GitHub Actions)*

---

## Questions this project answers

1. **Event incrementality** — How much lift did each campaign moment (Trailer 1, Trailer 2, the two delays, pre-order opening) drive in search demand, social volume, and attention?
2. **Attention decay** — What is the "half-life" of hype from each marketing asset?
3. **The scarcity strategy** — How does Rockstar's ultra-low asset cadence compare to typical AAA campaigns (RDR2, Cyberpunk 2077, Starfield), measured in earned attention per asset?
4. **Do delays hurt demand?** — GTA 6 was delayed twice. The data says something surprising.
5. **Live launch tracking** — Daily mention volume across Reddit, Hacker News, Wikipedia, and Google Trends, running through launch week.

## Data sources

| Source | What | How |
|---|---|---|
| Reddit (public JSON API) | Daily post mentions + r/GTA6 subscriber growth | `src/collect_mentions.py` |
| Hacker News (Algolia API) | Daily mention counts | `src/collect_mentions.py` |
| Wikipedia Pageviews API | Daily article views (attention proxy, full history) | `src/collect_wikipedia.py` |
| Google Trends (pytrends) | Search interest over time | `src/collect_trends.py` |
| Hand-curated event timeline | Campaign moments for annotation & incrementality windows | `data/events.csv` |

All sources are free and require no API keys.

## Architecture

```
GitHub Actions (daily cron, 06:00 UTC)
        │
        ├─ src/collect_mentions.py   ──►  data/mentions.csv
        ├─ src/collect_wikipedia.py  ──►  data/wikipedia_pageviews.csv
        └─ src/collect_trends.py     ──►  data/google_trends.csv
        │
        └─ auto-commit to this repo
                │
                ▼
Streamlit Community Cloud reads the CSVs ──► live dashboard
```

## Repo structure

```
├── src/                  # data collection scripts
├── data/                 # daily-updated CSVs (committed by CI)
├── dashboard/app.py      # Streamlit live dashboard
├── notebooks/            # analysis write-ups (incrementality, decay curves)
└── .github/workflows/    # daily collection cron
```

## Run it yourself

```bash
pip install -r requirements.txt
python src/collect_mentions.py
python src/collect_wikipedia.py
python src/collect_trends.py
streamlit run dashboard/app.py
```

## Analysis log

| Date | Post | Finding |
|---|---|---|
| *coming soon* | Pre-order spike analysis | |
| *coming soon* | Do delays kill hype? | |

---

*Built by Eden — performance marketer turned data analyst. [LinkedIn](https://linkedin.com/in/YOUR-PROFILE)*
