"""
app.py
-------
Streamlit dashboard for the Fixed Income Relative Value Screener.

Reuses the exact same data pipeline as main.py (src/data_loader.py,
src/analysis.py) so the dashboard and the CLI pipeline never drift out of
sync — this is a presentation layer on top of the existing analysis, not a
parallel implementation.

Run:
    streamlit run app.py
"""

import streamlit as st
import plotly.express as px

from src.data_loader import load_etf_data
from src.analysis import build_summary

st.set_page_config(page_title="Fixed Income Relative Value", layout="wide")

st.title("Fixed Income Relative Value Screener")
st.caption(
    "Live yield, volatility, and rich/cheap screening across ~20 real "
    "fixed-income ETFs. No hand-typed assumptions — every metric is "
    "recomputed from live data on each run."
)


@st.cache_data(ttl=3600, show_spinner="Downloading live ETF data...")
def get_data():
    data, mode = load_etf_data()
    df = build_summary(data)
    return df, data, mode


df, raw_data, mode = get_data()

if mode == "fallback":
    st.warning(
        "Live data unavailable — showing a clearly labeled synthetic sample. "
        "See README for details."
    )

st.sidebar.header("Filters")
segments = sorted(df["segment"].unique())
selected_segments = st.sidebar.multiselect("Segment", segments, default=segments)
filtered = df[df["segment"].isin(selected_segments)]

col1, col2, col3 = st.columns(3)
col1.metric("ETFs shown", len(filtered))
col2.metric("Median trailing yield", f"{filtered['current_yield_pct'].median():.2f}%")
col3.metric("Median yield / volatility", f"{filtered['yield_per_vol'].median():.2f}")

st.subheader("Ranked by yield per unit of volatility")
st.dataframe(
    filtered.sort_values("yield_per_vol", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Yield vs. volatility")
fig1 = px.scatter(
    filtered,
    x="current_vol_pct",
    y="current_yield_pct",
    color="segment",
    text="ticker",
    hover_data=["segment", "yield_per_vol"],
    labels={
        "current_vol_pct": "Realized annualized volatility (%)",
        "current_yield_pct": "Trailing 12-month yield (%)",
    },
)
fig1.update_traces(textposition="top center")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Current yield percentile vs. own trailing history")
sorted_pct = filtered.sort_values("yield_percentile_vs_own_history")
fig2 = px.bar(
    sorted_pct,
    x="yield_percentile_vs_own_history",
    y="ticker",
    orientation="h",
    color=sorted_pct["yield_percentile_vs_own_history"] > 50,
    color_discrete_map={True: "#4a7c59", False: "#8b2e2e"},
    labels={"yield_percentile_vs_own_history": "Percentile vs. own trailing history"},
)
fig2.add_vline(x=50, line_dash="dash", line_color="gray")
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Trailing yield history — single ticker")
ticker = st.selectbox("Choose a ticker", filtered["ticker"].tolist())
yield_series = raw_data[ticker]["yield_series"]
if yield_series is not None:
    hist_df = (yield_series * 100).reset_index()
    hist_df.columns = ["date", "trailing_yield_pct"]
    fig3 = px.line(
        hist_df,
        x="date",
        y="trailing_yield_pct",
        labels={"trailing_yield_pct": "Trailing 12-month yield (%)"},
    )
    st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Not investment advice — a demonstration of relative-value methodology "
    "applied to live data. See README for full methodology notes and limitations."
)
