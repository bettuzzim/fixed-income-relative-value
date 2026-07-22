"""
main.py
--------
End-to-end pipeline:
  1. Download real, live price and dividend data for ~20 fixed-income ETFs
     spanning Treasuries, IG/HY corporates, EM debt, bank loans, and more
  2. Derive current trailing yield, realized volatility, and each fund's
     yield percentile versus its own trailing history — no hand-typed
     assumptions anywhere
  3. Rank the universe by yield-per-unit-of-volatility
  4. Save charts and print the ranked summary

Also demonstrates the standalone DCF bond calculator (src/bond_pricer.py)
on one worked example using the live 20y+ Treasury ETF's yield as a
discount-rate proxy — a supplementary utility, not the main analysis.

Usage:
  python main.py
"""

import os
from src.data_loader import load_etf_data
from src.analysis import build_summary
from src.viz import plot_yield_vs_vol, plot_yield_percentile
from src.bond_pricer import fair_value, yield_to_maturity, macaulay_duration, modified_duration

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("\n### STEP 1 — Downloading live fixed-income ETF data ###")
    data, mode = load_etf_data()
    print(f"Mode: {mode}")

    print("\n### STEP 2-3 — Ranking by yield-per-unit-of-risk ###")
    df = build_summary(data)
    print(df.to_string(index=False))

    print("\n### STEP 4 — Charts ###")
    p1 = os.path.join(OUTPUT_DIR, "yield_vs_vol.png")
    plot_yield_vs_vol(df, p1)
    print(f"Saved: {p1}")

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
