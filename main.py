"""
main.py
--------
End-to-end pipeline:
  1. Download real, live price and dividend data for ~30 fixed-income ETFs
     spanning Treasuries, TIPS, IG/HY corporates, credit alternatives
     (bank loans, preferred, convertibles), EM debt, international, and
     municipal bonds — no hand-typed assumptions anywhere
  2. Download the live U.S. Treasury par yield curve from FRED (a second,
     independent data source) and use it to benchmark every fund at its
     own approximate duration
  3. Derive current trailing yield, realized volatility, each fund's yield
     percentile versus its own trailing history, and its spread to the
     duration-matched Treasury yield today
  4. Rank the universe by yield-per-unit-of-volatility
  5. Save four charts and print the ranked summary

Also demonstrates the standalone DCF bond calculator (src/bond_pricer.py)
on one worked example using the live 20y+ Treasury ETF's yield as a
discount-rate proxy — a supplementary utility, not the main analysis.

Usage:
  python main.py
"""

import os
from src.data_loader import load_etf_data
from src.treasury_curve import load_treasury_curve
from src.analysis import build_summary
from src.viz import (plot_yield_vs_vol, plot_yield_percentile,
                      plot_treasury_curve, plot_spread_to_treasury)
from src.bond_pricer import fair_value, macaulay_duration

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("\n### STEP 1 — Downloading live fixed-income ETF data (Yahoo Finance) ###")
    data, mode = load_etf_data()
    print(f"Mode: {mode}")

    print("\n### STEP 2 — Downloading the live Treasury par curve (FRED) ###")
    curve_today, curve_prior_year, curve_mode = load_treasury_curve()
    print(f"Mode: {curve_mode}")

    print("\n### STEP 3 — Ranking by yield-per-unit-of-risk and spread-to-curve ###")
    df = build_summary(data, treasury_curve=curve_today)
    print(df.to_string(index=False))

    print("\n### STEP 4 — Charts ###")
    p_curve = os.path.join(OUTPUT_DIR, "treasury_curve.png")
    plot_treasury_curve(curve_today, curve_prior_year, p_curve)
    print(f"Saved: {p_curve}")

    p1 = os.path.join(OUTPUT_DIR, "yield_vs_vol.png")
    plot_yield_vs_vol(df, p1)
    print(f"Saved: {p1}")

    p_spread = os.path.join(OUTPUT_DIR, "spread_to_treasury.png")
    plot_spread_to_treasury(df, p_spread)
    print(f"Saved: {p_spread}")

    p2 = os.path.join(OUTPUT_DIR, "yield_percentile.png")
    plot_yield_percentile(df, p2)
    print(f"Saved: {p2}")

    print("\n### Bonus — DCF bond calculator, worked example ###")
    print("(Standalone utility: values a hypothetical bond using a live")
    print(" long-term Treasury yield as the discount-rate proxy.)")

    tlt_row = df[df["ticker"] == "TLT"]
    if not tlt_row.empty:
        discount_rate = tlt_row.iloc[0]["current_yield_pct"] / 100
    else:
        discount_rate = 0.045  # fallback if TLT unavailable

    example_fv = fair_value(coupon_rate=0.04, face_value=1000,
                             years_to_maturity=10, discount_rate=discount_rate + 0.015)
    example_dur = macaulay_duration(0.04, 1000, 10, discount_rate + 0.015)
    print(f"Example: 10y bond, 4% coupon, discount rate = {discount_rate*100:.2f}% "
          f"(long Treasury proxy) + 150bps illustrative spread")
    print(f"  Fair value: {example_fv:.1f}")
    print(f"  Macaulay duration: {example_dur:.2f} years")

    print("\nDone.")


if __name__ == "__main__":
    main()
