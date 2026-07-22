"""
bond_pricer.py
----------------
Core bond mathematics:
  - fair_value(): discounted cash flow valuation given a discount rate
  - yield_to_maturity(): solves for the discount rate that reprices the
    bond to its observed market price (root-finding)
  - macaulay_duration() / modified_duration(): interest-rate sensitivity

Conventions follow the standard fixed-income textbook treatment (as in a
corporate finance / fixed income course): cash flows are coupon * face
value paid at each period, plus face value at maturity, discounted at a
periodic rate consistent with the payment frequency.

Simplifications (documented in the README):
  - No day-count convention nuances (assumes even periods)
  - No call/put optionality, no amortization
  - Flat discount rate per bond (risk-free at that maturity + credit
    spread), not a full risk-adjusted curve per cash flow date
"""

import numpy as np
from scipy.optimize import brentq


def _cash_flows(coupon_rate, face_value, years_to_maturity, freq):
    n_periods = int(round(years_to_maturity * freq))
    coupon_payment = coupon_rate * face_value / freq
    cash_flows = np.full(n_periods, coupon_payment)
    cash_flows[-1] += face_value
    return cash_flows


def fair_value(coupon_rate, face_value, years_to_maturity, discount_rate, freq=2):
    """Present value of a bond's cash flows at a given (annual) discount rate."""
    cash_flows = _cash_flows(coupon_rate, face_value, years_to_maturity, freq)
    periods = np.arange(1, len(cash_flows) + 1)
    periodic_rate = discount_rate / freq
    pv = np.sum(cash_flows / (1 + periodic_rate) ** periods)
    return pv


def yield_to_maturity(market_price, coupon_rate, face_value, years_to_maturity, freq=2):
    """Solves for the annual discount rate that reprices the bond to market_price."""
    def price_diff(rate):
        return fair_value(coupon_rate, face_value, years_to_maturity, rate, freq) - market_price

    try:
        return brentq(price_diff, 1e-6, 2.0)  # search between ~0% and 200%
    except ValueError:
        return np.nan  # no sign change found -> degenerate case


def macaulay_duration(coupon_rate, face_value, years_to_maturity, discount_rate, freq=2):
    cash_flows = _cash_flows(coupon_rate, face_value, years_to_maturity, freq)
    periods = np.arange(1, len(cash_flows) + 1)
    periodic_rate = discount_rate / freq
    discounted = cash_flows / (1 + periodic_rate) ** periods
    price = discounted.sum()
    weighted_time = (periods / freq) * discounted
    return weighted_time.sum() / price


def modified_duration(macaulay_dur, discount_rate, freq=2):
    return macaulay_dur / (1 + discount_rate / freq)
