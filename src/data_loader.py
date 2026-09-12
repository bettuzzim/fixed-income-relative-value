"""
data_loader.py
----------------
For each ETF in the universe, downloads real price history and real
dividend history via yfinance, then derives:
  - a trailing-12-month distribution yield time series (real dividends
    paid in the prior 365 days / price), computed fresh every run
  - realized annualized volatility from daily returns
  - the current trailing yield and its percentile rank within its own
    history (self-referential — no external assumption needed)

Each ticker is fetched independently and wrapped in try/except so that one
failed ticker does not break the whole run. If a ticker cannot be fetched
at all (e.g. no internet), it is skipped and reported; if the ENTIRE
universe fails, the module falls back to a small clearly-labeled synthetic
sample so the pipeline can still be demonstrated end-to-end.
"""

import time
import numpy as np
import pandas as pd

from src.etf_universe import ETF_UNIVERSE


def _trailing_yield_series(prices, dividends):
    """Builds a daily trailing-12-month yield series from real price and
    dividend history."""
    daily_div = dividends.reindex(prices.index, fill_value=0)
    trailing_div = daily_div.rolling("365D").sum()
    return trailing_div / prices


def load_etf_data(period="3y", pause=0.3):
    """
    Returns (data_dict, mode) where data_dict maps ticker -> {
        segment, name, current_yield, current_vol, yield_percentile,
        yield_series (for plotting), price_series
    }, and mode is "live" or "fallback".
    """
    try:
        import yfinance as yf
    except ImportError as e:
        print(f"[data_loader] WARNING: yfinance not installed ({e}).")
        print("[data_loader] Falling back to a SYNTHETIC illustrative sample.")
        return _synthetic_fallback(), "fallback"

    results = {}
    failures = []

    for ticker, meta in ETF_UNIVERSE.items():
        try:
            hist = yf.Ticker(ticker).history(period=period, actions=True)
            if hist.empty or "Dividends" not in hist.columns:
                raise ValueError("Empty history or no dividend data")

            prices = hist["Close"]
            dividends = hist["Dividends"]

            yield_series = _trailing_yield_series(prices, dividends).dropna()
            if yield_series.empty:
                raise ValueError("Could not compute trailing yield")

            daily_returns = prices.pct_change().dropna()
            vol = daily_returns.std() * np.sqrt(252)

            current_yield = yield_series.iloc[-1]
            percentile = (yield_series < current_yield).mean() * 100

            results[ticker] = {
                "segment": meta["segment"],
                "name": meta["name"],
                "family": meta["family"],
                "approx_duration_yrs": meta["approx_duration_yrs"],
                "current_yield": current_yield,
                "current_vol": vol,
                "yield_percentile": percentile,
                "yield_series": yield_series,
                "price_series": prices,
            }
            time.sleep(pause)

        except Exception as e:
            failures.append((ticker, f"{type(e).__name__}: {e}"))

    if failures:
        print(f"[data_loader] {len(failures)}/{len(ETF_UNIVERSE)} tickers failed: "
              f"{[f[0] for f in failures]}")

    if not results:
        print("[data_loader] WARNING: could not retrieve ANY live ETF data.")
        print("[data_loader] Falling back to a SYNTHETIC illustrative sample.")
        return _synthetic_fallback(), "fallback"

    print(f"[data_loader] Live data loaded for {len(results)}/{len(ETF_UNIVERSE)} ETFs.")
    return results, "live"


def _synthetic_fallback(seed=3):
    """Small synthetic sample, clearly labeled, used only if the entire
    live universe is unreachable (e.g. no internet at all)."""
    rng = np.random.default_rng(seed)
    segments = {
        "SIM_GOVT_SHORT": ("US Treasury (1-3y) [SIMULATED]", "US Treasury", 1.9),
        "SIM_GOVT_LONG": ("US Treasury (20y+) [SIMULATED]", "US Treasury", 16.5),
        "SIM_IG_CORP": ("IG Corporate (broad) [SIMULATED]", "IG Corporate", 8.4),
        "SIM_HY_CORP": ("HY Corporate (broad) [SIMULATED]", "HY Corporate", 3.2),
        "SIM_EM_DEBT": ("EM Debt (USD) [SIMULATED]", "EM Debt", 7.0),
    }
    base_yields = {"SIM_GOVT_SHORT": 0.045, "SIM_GOVT_LONG": 0.047,
                   "SIM_IG_CORP": 0.052, "SIM_HY_CORP": 0.078, "SIM_EM_DEBT": 0.068}
    base_vols = {"SIM_GOVT_SHORT": 0.02, "SIM_GOVT_LONG": 0.14,
                "SIM_IG_CORP": 0.07, "SIM_HY_CORP": 0.09, "SIM_EM_DEBT": 0.11}

    results = {}
    for ticker, (label, family, duration) in segments.items():
        dates = pd.date_range(end=pd.Timestamp.today(), periods=756, freq="B")
        yield_series = pd.Series(
            base_yields[ticker] + rng.normal(0, 0.003, size=len(dates)).cumsum() * 0.01,
            index=dates
        ).clip(lower=0.01)
        current_yield = yield_series.iloc[-1]
        percentile = (yield_series < current_yield).mean() * 100

        results[ticker] = {
            "segment": label,
            "name": label,
            "family": family,
            "approx_duration_yrs": duration,
            "current_yield": current_yield,
            "current_vol": base_vols[ticker],
            "yield_percentile": percentile,
            "yield_series": yield_series,
            "price_series": None,
        }
    return results
