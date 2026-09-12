"""
app.py
-------
Streamlit dashboard for the Fixed Income Relative Value Screener.

Reuses the exact same data pipeline as main.py (src/data_loader.py,
src/analysis.py, src/treasury_curve.py) so the dashboard and the CLI
pipeline never drift out of sync — this is a presentation layer on top of
the existing analysis, not a parallel implementation.

Run:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_etf_data
from src.treasury_curve import load_treasury_curve
from src.analysis import build_summary
from src.etf_universe import FAMILY_ORDER, FAMILY_COLORS

st.set_page_config(page_title="Fixed Income Relative Value", layout="wide")

st.title("Fixed Income Relative Value Screener")
st.caption(
    "Live yield, volatility, and rich/cheap screening across ~30 real "
    "fixed-income ETFs, benchmarked against the live Treasury curve. No "
    "hand-typed assumptions — every metric is recomputed from live data "
    "(Yahoo Finance + FRED) on each run."
)


@st.cache_data(ttl=3600, show_spinner="Downloading live ETF data...")
def get_data():
    data, mode = load_etf_data()
    curve_today, curve_prior_year, curve_mode = load_treasury_curve()
    df = build_summary(data, treasury_curve=curve_today)
    return df, data, mode, curve_today, curve_prior_year, curve_mode


df, raw_data, mode, curve_today, curve_prior_year, curve_mode = get_data()

if mode == "fallback":
    st.warning(
        "Live ETF data unavailable — showing a clearly labeled synthetic sample. "
        "See README for details."
    )
if curve_mode == "fallback":
    st.warning(
        "Live Treasury curve unavailable — spread-to-curve figures use an "
        "illustrative curve, not today's actual rates."
    )

st.sidebar.header("Filters")
families = st.sidebar.multiselect("Segment family", FAMILY_ORDER, default=FAMILY_ORDER)
filtered = df[df["family"].isin(families)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("ETFs shown", len(filtered))
col2.metric("Median trailing yield", f"{filtered['current_yield_pct'].median():.2f}%")
col3.metric("Median yield / volatility", f"{filtered['yield_per_vol'].median():.2f}")
col4.metric("Median spread to curve", f"{filtered['spread_to_treasury_bps'].median():.0f} bps")

st.subheader("Ranked by yield per unit of volatility")
st.dataframe(
    filtered.sort_values("yield_per_vol", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("U.S. Treasury par yield curve (source: FRED)")
fig_curve = go.Figure()
tenors_today = sorted(curve_today.keys())
fig_curve.add_trace(go.Scatter(x=tenors_today, y=[curve_today[t] for t in tenors_today],
                                mode="lines+markers", name="Today", line=dict(color="#2a78d6", width=3)))
if curve_prior_year:
    tenors_prior = sorted(curve_prior_year.keys())
    fig_curve.add_trace(go.Scatter(x=tenors_prior, y=[curve_prior_year[t] for t in tenors_prior],
                                    mode="lines+markers", name="~1 year ago",
                                    line=dict(color="#898781", width=2, dash="dash")))
fig_curve.update_layout(xaxis_title="Maturity (years)", yaxis_title="Par yield (%)", xaxis_type="log")
st.plotly_chart(fig_curve, use_container_width=True)

st.subheader("Yield vs. volatility, by segment family")
fig1 = px.scatter(
    filtered,
    x="current_vol_pct",
    y="current_yield_pct",
    color="family",
    category_orders={"family": FAMILY_ORDER},
    color_discrete_map=FAMILY_COLORS,
    text="ticker",
    hover_data=["segment", "yield_per_vol"],
    labels={
        "current_vol_pct": "Realized annualized volatility (%)",
        "current_yield_pct": "Trailing 12-month yield (%)",
    },
)
fig1.update_traces(textposition="top center")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Relative value vs. the live Treasury curve")
st.caption("Each fund's yield minus the curve interpolated at its own approximate duration — "
           "positive means yielding more than a same-duration Treasury today.")
sorted_spread = filtered.sort_values("spread_to_treasury_bps")
fig_spread = px.bar(
    sorted_spread,
    x="spread_to_treasury_bps",
    y="ticker",
    orientation="h",
    color=sorted_spread["spread_to_treasury_bps"] > 0,
    color_discrete_map={True: "#2a78d6", False: "#e34948"},
    labels={"spread_to_treasury_bps": "Spread to duration-matched Treasury (bps)"},
)
fig_spread.add_vline(x=0, line_color="#0b0b0b")
fig_spread.update_layout(showlegend=False)
st.plotly_chart(fig_spread, use_container_width=True)

st.subheader("Current yield percentile vs. own trailing history")
sorted_pct = filtered.sort_values("yield_percentile_vs_own_history")
fig2 = px.bar(
    sorted_pct,
    x="yield_percentile_vs_own_history",
    y="ticker",
    orientation="h",
    color=sorted_pct["yield_percentile_vs_own_history"] > 50,
    color_discrete_map={True: "#2a78d6", False: "#e34948"},
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
