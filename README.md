# Fixed Income Relative Value Screener

Systematic relative-value analysis across a live universe of approximately 20 exchange-traded fixed-income funds — U.S. Treasuries, investment-grade and high-yield corporates, emerging market debt, and bank loans. The tool ranks the universe by risk-adjusted yield and identifies which segments are trading rich or cheap relative to their own historical distribution.

The analysis is fully data-driven: no assumptions are hard-coded. Every execution retrieves current prices and dividend distributions and recomputes all metrics from source.

## Methodology

1. **Data acquisition** — live price and dividend history for approximately 20 bond ETFs via `yfinance`, spanning short- and long-duration Treasuries, TIPS, investment-grade and high-yield corporates, bank loans, USD- and local-currency emerging market debt, international government bonds, and broad aggregates.

2. **Derived metrics, recomputed on every run**
   - **Trailing twelve-month yield** — realized distributions over the preceding 365 days, divided by current price
   - **Realized volatility** — annualized standard deviation of daily returns
   - **Yield percentile versus own history** — the current yield's position within that fund's trailing distribution, benchmarked against itself rather than an external index

3. **Ranking** — the universe is ordered by yield per unit of volatility, a risk-adjusted compensation measure applied consistently across heterogeneous segments.

4. **Supplementary module** — a standalone discounted-cash-flow bond calculator (`src/bond_pricer.py`) values a hypothetical bond using a live long-term Treasury yield as the discount-rate proxy.

## Project structure

```
fixed-income-rv/
├── main.py                  # pipeline orchestration
├── requirements.txt
├── src/
│   ├── etf_universe.py      # ETF universe definition and segment classification
│   ├── data_loader.py       # data acquisition, yield and volatility computation
│   ├── analysis.py          # ranked summary construction
│   ├── viz.py                # chart generation
│   └── bond_pricer.py       # standalone DCF / YTM / duration calculator
└── outputs/                  # generated charts (created at runtime)
```

## Execution

```bash
pip install -r requirements.txt
python main.py
```

Requires an active internet connection. Individual ticker failures (e.g., transient rate limiting) are handled gracefully and excluded without interrupting the run. If the data source is entirely unreachable, the pipeline falls back to a clearly labeled synthetic sample so the codebase remains reviewable end-to-end.

## Output

**Yield versus volatility across the universe**

![Yield vs Vol](outputs/yield_vs_vol.png)

**Current yield versus own trailing history**

![Yield Percentile](outputs/yield_percentile.png)

## Methodology notes and limitations

- **ETF distribution yield as a proxy for yield-to-maturity.** Trailing twelve-month distribution yield is a standard practitioner approximation, but it reflects dividends already paid rather than the fund's current portfolio yield-to-maturity, and can be distorted by special distributions or portfolio turnover. Provider-reported SEC yield or YTM would be more precise where reliably available.
- **Realized volatility as a proxy for duration risk.** Price volatility captures interest-rate and credit risk jointly, not duration in isolation. It is a practical risk measure, not a substitute for provider-published effective duration.
- **USD-centric universe.** The current universe is predominantly USD-denominated and US-listed. Extension to EUR-denominated instruments (Bund, OAT, BTP) is a natural next step for a euro-based mandate.
- **Historical window.** The three-year lookback used for percentile ranking is a modeling choice; a different window would shift the classification of "rich" versus "cheap."
- **Not investment advice.** This is a demonstration of relative-value methodology applied to live data, not a portfolio recommendation.

## Tech stack

Python · pandas · numpy · yfinance · matplotlib

## Author

Marco Bettuzzi
Economics and Statistics, University of Turin
[github.com/bettuzzim](https://github.com/bettuzzim)
