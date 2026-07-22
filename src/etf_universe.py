"""
etf_universe.py
------------------
A real, exchange-traded universe of fixed-income ETFs spanning the main
segments a fixed-income allocator would consider. These are genuine
securities with live prices and dividend histories on Yahoo Finance — no
synthetic or hand-typed data anywhere in this module.

Segment labels are used for grouping/coloring in charts and are a
simplification of each fund's actual mandate (see each provider's
factsheet for the precise benchmark and constituents).
"""

ETF_UNIVERSE = {
    "SHY":  {"segment": "US Treasury (1-3y)",        "name": "iShares 1-3 Year Treasury Bond ETF"},
    "IEI":  {"segment": "US Treasury (3-7y)",         "name": "iShares 3-7 Year Treasury Bond ETF"},
    "IEF":  {"segment": "US Treasury (7-10y)",        "name": "iShares 7-10 Year Treasury Bond ETF"},
    "TLT":  {"segment": "US Treasury (20y+)",         "name": "iShares 20+ Year Treasury Bond ETF"},
    "TIP":  {"segment": "US TIPS (inflation-linked)", "name": "iShares TIPS Bond ETF"},
    "IGSB": {"segment": "IG Corporate (short)",       "name": "iShares Short-Term Corp Bond ETF"},
    "VCIT": {"segment": "IG Corporate (intermediate)","name": "Vanguard Interm-Term Corp Bond ETF"},
    "LQD":  {"segment": "IG Corporate (broad)",       "name": "iShares iBoxx IG Corp Bond ETF"},
    "IGLB": {"segment": "IG Corporate (long)",        "name": "iShares Long-Term Corp Bond ETF"},
    "SHYG": {"segment": "HY Corporate (short)",       "name": "iShares 0-5 Year HY Corp Bond ETF"},
    "HYG":  {"segment": "HY Corporate (broad)",       "name": "iShares iBoxx HY Corp Bond ETF"},
    "JNK":  {"segment": "HY Corporate (broad)",       "name": "SPDR Bloomberg HY Bond ETF"},
    "BKLN": {"segment": "Bank Loans (floating rate)", "name": "Invesco Senior Loan ETF"},
    "EMB":  {"segment": "EM Debt (USD)",              "name": "iShares JPM EM Bond ETF"},
    "PCY":  {"segment": "EM Debt (USD)",              "name": "Invesco EM Sovereign Debt ETF"},
    "EMLC": {"segment": "EM Debt (local currency)",   "name": "VanEck EM Local Currency Bond ETF"},
    "BWX":  {"segment": "International Govt (ex-US)", "name": "SPDR Intl Treasury Bond ETF"},
    "BNDX": {"segment": "International Aggregate",    "name": "Vanguard Total Intl Bond ETF"},
    "AGG":  {"segment": "US Aggregate (broad)",       "name": "iShares Core US Aggregate Bond ETF"},
    "MUB":  {"segment": "US Municipal",               "name": "iShares National Muni Bond ETF"},
}
