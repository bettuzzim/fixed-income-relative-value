"""
treasury_curve.py
--------------------
Second live data source (alongside Yahoo Finance): the U.S. Treasury par
yield curve from FRED (Federal Reserve Economic Data), fetched as public
CSV — no API key required.

This is what turns the ETF ranking from "cheap/rich versus its own past"
into "cheap/rich versus the current risk-free curve at a matched duration"
— the standard relative-value framework (spread over the curve) rather
than a purely self-referential one.
"""

import io
import urllib.request

import numpy as np
import pandas as pd

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# FRED series id -> tenor in years, spanning the on-the-run par curve.
TENORS = {
    "DGS1MO": 1 / 12,
    "DGS3MO": 3 / 12,
    "DGS6MO": 6 / 12,
    "DGS1":   1.0,
    "DGS2":   2.0,
    "DGS3":   3.0,
    "DGS5":   5.0,
    "DGS7":   7.0,
    "DGS10":  10.0,
    "DGS20":  20.0,
    "DGS30":  30.0,
}


def _fetch_series(series_id, timeout=10):
    """Downloads one FRED series as a CSV and returns it as a Series indexed
    by date. FRED marks missing observations with '.', dropped here."""
    url = FRED_CSV.format(series_id=series_id)
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    df = pd.read_csv(io.StringIO(raw))
    df.columns = ["date", "value"]
    df = df[df["value"] != "."]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = df["value"].astype(float)
    return df.set_index("date")["value"]


def load_treasury_curve():
    """
    Returns (curve_today, curve_prior_year, mode):
      - curve_today: dict {tenor_years: yield_pct}, latest available observation
      - curve_prior_year: same shape, ~1 year earlier — for a "how has the
        curve shifted" comparison
      - mode: "live" or "fallback"

    Falls back to a small clearly-labeled illustrative curve if FRED is
    unreachable, so the pipeline still runs end-to-end offline.
    """
    try:
        today, year_ago = {}, {}
        for series_id, tenor in TENORS.items():
            s = _fetch_series(series_id)
            today[tenor] = float(s.iloc[-1])
            one_year_cutoff = s.index[-1] - pd.Timedelta(days=365)
            prior = s[s.index <= one_year_cutoff]
            if not prior.empty:
                year_ago[tenor] = float(prior.iloc[-1])

        if not today:
            raise ValueError("No tenors retrieved from FRED")

        return today, year_ago, "live"

    except Exception as e:
        print(f"[treasury_curve] WARNING: could not retrieve live FRED curve "
              f"({type(e).__name__}: {e}). Falling back to an illustrative curve.")
        fallback = {1/12: 4.3, 0.25: 4.3, 0.5: 4.2, 1: 4.0, 2: 3.8,
                    3: 3.8, 5: 3.9, 7: 4.1, 10: 4.3, 20: 4.7, 30: 4.6}
        return fallback, {}, "fallback"


def interpolated_yield(curve, duration_yrs):
    """Linearly interpolates the par curve to estimate the yield at an
    arbitrary duration — used to benchmark each ETF against a duration-
    matched point on the risk-free curve rather than a single fixed tenor."""
    tenors = np.array(sorted(curve.keys()))
    yields = np.array([curve[t] for t in tenors])
    duration_yrs = min(max(duration_yrs, tenors.min()), tenors.max())
    return float(np.interp(duration_yrs, tenors, yields))
