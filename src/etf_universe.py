"""
etf_universe.py
------------------
A real, exchange-traded universe of fixed-income ETFs spanning the main
segments a fixed-income allocator would consider. These are genuine
securities with live prices and dividend histories on Yahoo Finance — no
synthetic or hand-typed data anywhere in this module.

Each entry carries:
  - segment: fine-grained label used in the ranking table
  - name: the fund's full name
  - family: one of 8 broad groupings, used for chart color coding (kept to
    8 so every chart uses a fixed, colorblind-checked categorical palette
    instead of an uncapped rainbow of segments)
  - approx_duration_yrs: an illustrative effective-duration bucket based on
    published fund factsheets (rounded, not live). Used only to map each
    fund to the nearest point on the live Treasury par curve for a
    duration-matched spread estimate — see src/treasury_curve.py. This is
    a simplification: a fund's actual effective duration moves with rates
    and portfolio composition; this is a fixed anchor, not a daily figure.
"""

ETF_UNIVERSE = {
    # --- US Treasury ---------------------------------------------------
    "SGOV": {"segment": "US Treasury (0-3mo)",        "name": "iShares 0-3 Month Treasury Bond ETF",       "family": "US Treasury", "approx_duration_yrs": 0.2},
    "SHY":  {"segment": "US Treasury (1-3y)",         "name": "iShares 1-3 Year Treasury Bond ETF",        "family": "US Treasury", "approx_duration_yrs": 1.9},
    "IEI":  {"segment": "US Treasury (3-7y)",         "name": "iShares 3-7 Year Treasury Bond ETF",        "family": "US Treasury", "approx_duration_yrs": 4.4},
    "IEF":  {"segment": "US Treasury (7-10y)",        "name": "iShares 7-10 Year Treasury Bond ETF",       "family": "US Treasury", "approx_duration_yrs": 7.4},
    "TLT":  {"segment": "US Treasury (20y+)",         "name": "iShares 20+ Year Treasury Bond ETF",        "family": "US Treasury", "approx_duration_yrs": 16.5},

    # --- TIPS (inflation-linked) ----------------------------------------
    "VTIP": {"segment": "US TIPS (0-5y)",             "name": "Vanguard Short-Term Infl-Prot Secs ETF",    "family": "TIPS", "approx_duration_yrs": 2.5},
    "TIP":  {"segment": "US TIPS (broad)",            "name": "iShares TIPS Bond ETF",                     "family": "TIPS", "approx_duration_yrs": 7.5},

    # --- IG Corporate & agency credit ------------------------------------
    "IGSB": {"segment": "IG Corporate (short)",       "name": "iShares Short-Term Corp Bond ETF",          "family": "IG Corporate", "approx_duration_yrs": 1.9},
    "FLOT": {"segment": "IG Floating Rate",           "name": "iShares Floating Rate Bond ETF",            "family": "IG Corporate", "approx_duration_yrs": 0.1},
    "VCIT": {"segment": "IG Corporate (intermediate)","name": "Vanguard Interm-Term Corp Bond ETF",        "family": "IG Corporate", "approx_duration_yrs": 6.0},
    "LQD":  {"segment": "IG Corporate (broad)",       "name": "iShares iBoxx IG Corp Bond ETF",            "family": "IG Corporate", "approx_duration_yrs": 8.4},
    "MBB":  {"segment": "Agency MBS",                 "name": "iShares MBS ETF",                           "family": "IG Corporate", "approx_duration_yrs": 5.8},
    "IGLB": {"segment": "IG Corporate (long)",        "name": "iShares Long-Term Corp Bond ETF",           "family": "IG Corporate", "approx_duration_yrs": 15.0},

    # --- HY Corporate -----------------------------------------------------
    "SHYG": {"segment": "HY Corporate (short)",       "name": "iShares 0-5 Year HY Corp Bond ETF",         "family": "HY Corporate", "approx_duration_yrs": 2.0},
    "HYG":  {"segment": "HY Corporate (broad)",       "name": "iShares iBoxx HY Corp Bond ETF",            "family": "HY Corporate", "approx_duration_yrs": 3.2},
    "JNK":  {"segment": "HY Corporate (broad)",       "name": "SPDR Bloomberg HY Bond ETF",                "family": "HY Corporate", "approx_duration_yrs": 3.5},
    "ANGL": {"segment": "HY Fallen Angels",           "name": "VanEck Fallen Angel HY Bond ETF",           "family": "HY Corporate", "approx_duration_yrs": 4.2},

    # --- Credit alternatives (bank loans, preferred, convertibles) -------
    "BKLN": {"segment": "Bank Loans (floating rate)", "name": "Invesco Senior Loan ETF",                   "family": "Credit Alternatives", "approx_duration_yrs": 0.3},
    "PFF":  {"segment": "Preferred Securities",       "name": "iShares Preferred & Income Securities ETF", "family": "Credit Alternatives", "approx_duration_yrs": 4.0},
    "CWB":  {"segment": "Convertible Securities",     "name": "SPDR Bloomberg Convertible Secs ETF",       "family": "Credit Alternatives", "approx_duration_yrs": 3.0},

    # --- EM Debt ------------------------------------------------------------
    "EMB":  {"segment": "EM Sovereign Debt (USD)",    "name": "iShares JPM EM Bond ETF",                   "family": "EM Debt", "approx_duration_yrs": 7.0},
    "PCY":  {"segment": "EM Sovereign Debt (USD)",    "name": "Invesco EM Sovereign Debt ETF",             "family": "EM Debt", "approx_duration_yrs": 8.0},
    "EMLC": {"segment": "EM Debt (local currency)",   "name": "VanEck EM Local Currency Bond ETF",         "family": "EM Debt", "approx_duration_yrs": 5.0},
    "CEMB": {"segment": "EM Corporate Debt (USD)",    "name": "iShares EM Corporate Bond ETF",             "family": "EM Debt", "approx_duration_yrs": 5.5},
    "HYEM": {"segment": "EM High Yield Debt (USD)",   "name": "VanEck EM High Yield Bond ETF",             "family": "EM Debt", "approx_duration_yrs": 4.0},

    # --- International & broad aggregate -----------------------------------
    "BWX":  {"segment": "International Govt (ex-US)", "name": "SPDR Intl Treasury Bond ETF",               "family": "International & Aggregate", "approx_duration_yrs": 7.5},
    "BNDX": {"segment": "International Aggregate",     "name": "Vanguard Total Intl Bond ETF",              "family": "International & Aggregate", "approx_duration_yrs": 7.0},
    "AGG":  {"segment": "US Aggregate (broad)",        "name": "iShares Core US Aggregate Bond ETF",        "family": "International & Aggregate", "approx_duration_yrs": 6.0},

    # --- Municipal -----------------------------------------------------------
    "MUB":  {"segment": "US Municipal (IG)",           "name": "iShares National Muni Bond ETF",            "family": "Municipal", "approx_duration_yrs": 6.5},
    "HYD":  {"segment": "US Municipal (HY)",           "name": "VanEck HY Muni ETF",                        "family": "Municipal", "approx_duration_yrs": 6.0},
}

# Fixed, colorblind-checked 8-hue order (dataviz skill default palette).
# Never cycled and never reassigned per-run — each family always maps to
# the same slot so a color always means the same thing across charts.
FAMILY_ORDER = [
    "US Treasury",
    "TIPS",
    "IG Corporate",
    "HY Corporate",
    "Credit Alternatives",
    "EM Debt",
    "International & Aggregate",
    "Municipal",
]

FAMILY_COLORS = {
    "US Treasury":               "#2a78d6",  # slot 1 — blue
    "TIPS":                      "#eb6834",  # slot 2 — orange
    "IG Corporate":              "#1baf7a",  # slot 3 — aqua
    "HY Corporate":              "#eda100",  # slot 4 — yellow
    "Credit Alternatives":       "#e87ba4",  # slot 5 — magenta
    "EM Debt":                   "#008300",  # slot 6 — green
    "International & Aggregate": "#4a3aa7",  # slot 7 — violet
    "Municipal":                 "#e34948",  # slot 8 — red
}
