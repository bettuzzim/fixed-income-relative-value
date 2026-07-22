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
"""

import pandas as pd


def build_summary(data):
    rows = []
    for ticker, d in data.items():
        rows.append({
            "ticker": ticker,
            "segment": d["segment"],
            "current_yield_pct": round(d["current_yield"] * 100, 2),
            "current_vol_pct": round(d["current_vol"] * 100, 2),
            "yield_per_vol": round(d["current_yield"] / d["current_vol"], 2) if d["current_vol"] > 0 else float("nan"),
            "yield_percentile_vs_own_history": round(d["yield_percentile"], 1),
        })
    df = pd.DataFrame(rows).sort_values("yield_per_vol", ascending=False).reset_index(drop=True)
    return df
