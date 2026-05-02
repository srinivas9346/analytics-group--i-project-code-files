"""Interactive Streamlit dashboard for accident risk analysis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import weather_correlation
from src.config import CONFIG
from src.visualization import create_plotly_hotspot_map

st.set_page_config(page_title="Traffic Accident Risk Analysis (Ireland)", layout="wide")
st.title("Traffic Accident Risk Analysis and Prediction (Ireland)")

data_path = f"{CONFIG.processed_data_dir}/integrated_accident_weather.csv"
df = pd.read_csv(data_path)
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

st.sidebar.header("Filters")
counties = st.sidebar.multiselect("County", sorted(df["county"].unique()), default=sorted(df["county"].unique()))
df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
date_min = df["date_dt"].min()
date_max = df["date_dt"].max()
st.sidebar.caption(f"Data available: {date_min.date()} to {date_max.date()}")
date_range = st.sidebar.slider(
    "Date range",
    min_value=date_min.to_pydatetime(),
    max_value=date_max.to_pydatetime(),
    value=(date_min.to_pydatetime(), date_max.to_pydatetime()),
    format="YYYY-MM-DD",
)
rain_only = st.sidebar.checkbox("Show rainy condition accidents only")

filtered = df[df["county"].isin(counties)].copy()
start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered = filtered[(filtered["date_dt"] >= start_dt) & (filtered["date_dt"] <= end_dt)].copy()
if rain_only:
    filtered = filtered[filtered["rain_flag"] == 1]

col1, col2, col3 = st.columns(3)
col1.metric("Accidents", f"{len(filtered):,}")
col2.metric("Avg Severity", f"{filtered['severity'].mean():.2f}")
col3.metric("Avg Weather Impact", f"{filtered['weather_impact_score'].mean():.2f}")

st.subheader("Accident Time Series")
ts = filtered.groupby("date", as_index=False).agg(accidents=("accident_id", "count"))
ts["date"] = pd.to_datetime(ts["date"])
st.plotly_chart(px.line(ts, x="date", y="accidents", title="Daily Accident Counts"), width="stretch")

st.subheader("Accidents by Severity")
sev = filtered.groupby("severity", as_index=False).agg(accidents=("accident_id", "count"))
st.plotly_chart(
    px.bar(sev, x="severity", y="accidents", color="severity", title="Severity Distribution"),
    width="stretch",
)

st.subheader("Geospatial Hotspot Map")
st.plotly_chart(create_plotly_hotspot_map(filtered), width="stretch")

st.subheader("Correlation Matrix")
corr = weather_correlation(filtered)
heatmap_fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", title="Correlation Matrix")
st.plotly_chart(heatmap_fig, width="stretch")

