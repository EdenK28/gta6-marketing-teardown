"""GTA 6 Live Mentions Dashboard — Streamlit app.

Reads the CSVs that GitHub Actions updates daily. Deploy free on
Streamlit Community Cloud pointed at this repo.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(page_title="GTA 6 Hype Tracker", page_icon="🎮", layout="wide")
st.title("🎮 GTA 6 Marketing Teardown — Live Mentions Dashboard")

LAUNCH = datetime(2026, 11, 19)
days_left = (LAUNCH - datetime.utcnow()).days
st.caption(
    f"**{days_left} days to launch** (Nov 19, 2026) · Data refreshes daily via "
    "GitHub Actions · Built by a performance marketer analyzing the biggest "
    "launch campaign in entertainment history"
)


@st.cache_data(ttl=3600)
def load(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["date"])
    return df


mentions = load("mentions.csv")
wiki = load("wikipedia_pageviews.csv")
trends = load("google_trends.csv")
events = load("events.csv")


def add_event_lines(fig: go.Figure, df_events: pd.DataFrame) -> go.Figure:
    colors = {"trailer": "#e74c3c", "delay": "#f39c12",
              "commerce": "#2ecc71", "launch": "#9b59b6", "announcement": "#95a5a6"}
    for _, row in df_events.iterrows():
        fig.add_vline(x=row["date"], line_dash="dot",
                      line_color=colors.get(row["category"], "#95a5a6"), opacity=0.6)
        fig.add_annotation(x=row["date"], y=1.02, yref="paper", text=row["event"][:28],
                           showarrow=False, textangle=-45, font=dict(size=9))
    return fig


# ── KPI row ──────────────────────────────────────────────────────────────
if not mentions.empty:
    latest = mentions[mentions["date"] == mentions["date"].max()]
    cols = st.columns(4)
    metric_map = [
        ("reddit", "posts_24h", "Reddit posts (24h)"),
        ("reddit", "r_gta6_subscribers", "r/GTA6 subscribers"),
        ("hackernews", "mentions_24h", "HN mentions (24h)"),
    ]
    for i, (source, metric, label) in enumerate(metric_map):
        row = latest[(latest["source"] == source) & (latest["metric"] == metric)]
        if not row.empty:
            value = int(row["value"].iloc[0])
            # delta vs. previous day
            hist = mentions[(mentions["source"] == source) & (mentions["metric"] == metric)]
            hist = hist.sort_values("date")
            delta = value - int(hist["value"].iloc[-2]) if len(hist) > 1 else None
            cols[i].metric(label, f"{value:,}", delta=f"{delta:+,}" if delta is not None else None)
    cols[3].metric("Days to launch", days_left)

st.divider()

# ── Daily mentions by source ─────────────────────────────────────────────
st.subheader("Daily mention volume by source")
if mentions.empty:
    st.info("No mention data yet — run `python src/collect_mentions.py` or wait for the daily cron.")
else:
    vol = mentions[mentions["metric"].isin(["posts_24h", "mentions_24h"])]
    fig = px.line(vol, x="date", y="value", color="source", markers=True,
                  labels={"value": "mentions / day"})
    if not events.empty:
        fig = add_event_lines(fig, events[events["date"] >= vol["date"].min()])
    st.plotly_chart(fig, use_container_width=True)

# ── Long-run attention: Wikipedia ────────────────────────────────────────
st.subheader("Long-run attention: Wikipedia daily pageviews")
if wiki.empty:
    st.info("Run `python src/collect_wikipedia.py` to pull the full history.")
else:
    fig = px.area(wiki, x="date", y="pageviews")
    fig.update_traces(line_color="#3498db")
    if not events.empty:
        fig = add_event_lines(fig, events)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Every spike maps to a campaign event. This is what earned attention "
        "looks like when you release two trailers in 2.5 years."
    )

# ── Google Trends ────────────────────────────────────────────────────────
st.subheader("Google search interest")
if trends.empty:
    st.info("Run `python src/collect_trends.py` to pull search interest.")
else:
    fig = px.line(trends, x="date", y="search_interest")
    fig.update_traces(line_color="#2ecc71")
    if not events.empty:
        fig = add_event_lines(fig, events)
    st.plotly_chart(fig, use_container_width=True)

# ── r/GTA6 community growth ──────────────────────────────────────────────
subs = mentions[mentions["metric"] == "r_gta6_subscribers"] if not mentions.empty else pd.DataFrame()
if not subs.empty and len(subs) > 1:
    st.subheader("r/GTA6 community growth")
    st.plotly_chart(px.line(subs, x="date", y="value",
                            labels={"value": "subscribers"}), use_container_width=True)

st.divider()
st.markdown(
    "**About:** I ran mobile UA campaigns for 6+ years. This dashboard applies "
    "performance-marketing analysis (incrementality, attention decay, demand curves) "
    "to Rockstar's GTA 6 campaign. Full analysis in the "
    "[GitHub repo](https://github.com/YOUR-USERNAME/gta6-marketing-teardown)."
)
