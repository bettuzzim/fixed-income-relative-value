"""
analysis.py
-------------
Turns the per-ticker data dict into a ranked summary table:
  - current_yield, current_vol, yield_percentile (all real/derived, no
    hand-typed assumptions)
  - yield_per_vol: current_yield / current_vol, a simple risk-adjusted
    compensation measure — how much yield you get per unit of realized
    volatility, comparable across very different segments (a 2% yield at
    2% vol may be more attractive than an 8% yield at 12% vol)
  - spread_to_treasury_bps: current yield minus the live Treasury par
    curve interpolated at the fund's approximate duration — a
    duration-matched relative-value measure against the actual risk-free
    curve today, not just the fund's own trailing history
"""

import pandas as pd

from src.treasury_curve import interpolated_yield


def build_summary(data, treasury_curve=None):
    rows = []
    for ticker, d in data.items():
        row = {
            "ticker": ticker,
            "segment": d["segment"],
            "family": d["family"],
            "approx_duration_yrs": d["approx_duration_yrs"],
            "current_yield_pct": round(d["current_yield"] * 100, 2),
            "current_vol_pct": round(d["current_vol"] * 100, 2),
            "yield_per_vol": round(d["current_yield"] / d["current_vol"], 2) if d["current_vol"] > 0 else float("nan"),
            "yield_percentile_vs_own_history": round(d["yield_percentile"], 1),
        }
        if treasury_curve:
            benchmark_yield_pct = interpolated_yield(treasury_curve, d["approx_duration_yrs"])
            row["treasury_benchmark_pct"] = round(benchmark_yield_pct, 2)
            row["spread_to_treasury_bps"] = round((d["current_yield"] * 100 - benchmark_yield_pct) * 100, 0)
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("yield_per_vol", ascending=False).reset_index(drop=True)
    return df
