# Fixed Income Relative Value Screener

Screens a real, live universe of ~20 exchange-traded fixed-income funds
(Treasuries, investment-grade and high-yield corporates, emerging market
debt, bank loans, and more) to find where the market currently offers the
best compensation (yield) per unit of risk (volatility) — and whether each
segment is currently rich or cheap relative to **its own trailing history**.

No hand-typed assumptions anywhere in the core analysis: every run pulls
fresh prices and dividend distributions and recomputes everything from
scratch.

Built as an independent project applying fixed-income and relative-value
concepts to real, live market data.

## What it does

1. **Live data** — downloads real price and dividend history for ~20 bond
   ETFs via `yfinance`, spanning US Treasuries (short to long), TIPS,
   investment-grade and high-yield corporates, bank loans, EM debt
   (USD and local currency), international government bonds, and broad
   aggregates.
2. **Derived metrics, computed fresh every run**:
   - **Trailing-12-month yield** — real dividends paid in the last 365
     days, divided by the current price
   - **Realized volatility** — annualized standard deviation of daily
     returns
   - **Yield percentile vs. own history** — where today's yield sits
     within that same fund's own trailing yield history (no external
     benchmark needed — each fund is compared only to itself)
3. **Ranking** — sorts the universe by yield-per-unit-of-volatility, a
   simple risk-adjusted compensation measure comparable across very
   different segments.
4. **Bonus utility** — the standalone DCF bond calculator
   (`src/bond_pricer.py`, carried over from an earlier version of this
   project) values a hypothetical bond using a live long-term Treasury
   yield as the discount-rate proxy, as a worked example.

## Project structure

```
fixed-income-rv/
├── main.py                  # orchestrates the full pipeline
├── requirements.txt
├── src/
│   ├── etf_universe.py       # the ~20 real ETF tickers and segments
│   ├── data_loader.py        # downloads live data, computes yield/vol
│   ├── analysis.py           # builds the ranked summary table
│   ├── viz.py                # charts
│   └── bond_pricer.py        # standalone DCF/YTM/duration calculator
└── outputs/                  # generated charts (created on run)
```

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Requires an internet connection to fetch live ETF data. If a handful of
tickers fail (temporary rate limits, etc.) they are skipped individually
and the rest of the universe still runs. If the **entire** universe is
unreachable (e.g. no internet at all), the pipeline falls back to a small,
clearly-labeled synthetic sample so the code can still be reviewed
end-to-end.

## Example output

**Yield vs. volatility across the universe:**

![Yield vs Vol](outputs/yield_vs_vol.png)

**Current yield vs. own trailing history:**

![Yield Percentile](outputs/yield_percentile.png)

## Methodology notes and limitations

- **ETF yield as a proxy, not a precise bond-level YTM**: the
  trailing-12-month distribution yield is a common practitioner shortcut,
  but it lags reality somewhat (it reflects dividends already paid, not
  the fund's current portfolio yield-to-maturity) and can be distorted by
  special distributions or changes in the underlying portfolio.
  Fund-reported "SEC yield" or "YTM", where available from the provider,
  would be more precise but is not reliably available via free APIs.
- **Volatility as a risk proxy for duration**: realized price volatility
  captures interest-rate *and* credit risk together, not duration alone —
  useful as a practical risk measure, but not a substitute for a fund's
  actual effective duration (published by the provider, not by this tool).
- **US-dollar-centric universe**: most of these ETFs are USD-denominated
  and US-listed; a euro-based private bank would also consider
  Bund/OAT/BTP-denominated instruments — this is a natural extension
  (e.g. adding London-listed EUR bond ETFs via yfinance).
- **Historical window (3 years)** for the percentile calculation is a
  modeling choice — a longer or shorter window would shift what counts as
  "rich" or "cheap."
- **Not investment advice** — a demonstration of the relative-value
  method using real data, not a portfolio recommendation.

## Tech stack

Python · pandas · numpy · yfinance · matplotlib

## Author

Marco Bettuzzi — Economics and Statistics student, University of Turin
