"""
viz.py
-------
Four charts, built on a shared style (see `_apply_style`) so the repo reads
as one system rather than four one-off matplotlib defaults. Colors follow a
fixed, colorblind-checked categorical order (dataviz method, see
etf_universe.FAMILY_COLORS) and a validated diverging pair (blue<->red,
neutral gray midpoint) wherever the value has a "which side of a baseline"
meaning — never an arbitrary red/green pick.

  1. Treasury par curve — today vs. one year ago (the second live data
     source, FRED, and the benchmark the relative-value chart is measured
     against).
  2. Bubble chart of current yield vs. volatility, colored by broad segment
     family — where the best compensation per unit of risk currently sits.
  3. Spread to duration-matched Treasury — the flagship relative-value
     view: each fund's yield minus the live curve at its own duration,
     diverging around zero.
  4. Horizontal bar chart of each fund's yield percentile versus its own
     trailing history — self-referential richness/cheapness, independent
     of the curve-based measure above.

Note on chart 2's color count: 8 segment families exceed the 3-category cap
that a scatter/bubble form can carry while staying pairwise colorblind-safe
under every combination (see dataviz skill, all-pairs check). Every point
is also directly labeled with its ticker, so identification never depends
on color alone — but a colorblind reader relying on hue alone could still
confuse two of the eight families in that one chart. Capping to 3 families
or faceting into small multiples would close that gap; left as a known
tradeoff rather than done silently.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from src.etf_universe import FAMILY_COLORS, FAMILY_ORDER
from src.treasury_curve import TENORS

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"

DIVERGING_POSITIVE = "#2a78d6"   # blue — cheap side (yielding more than benchmark)
DIVERGING_NEGATIVE = "#e34948"   # red — rich side (yielding less than benchmark)
DIVERGING_NEUTRAL = "#f0efec"


def _apply_style(ax, fig):
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=INK_SECONDARY, labelsize=8.5)
    ax.xaxis.label.set_color(INK_SECONDARY)
    ax.yaxis.label.set_color(INK_SECONDARY)
    ax.title.set_color(INK_PRIMARY)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)
    ax.grid(color=GRIDLINE, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)


def plot_treasury_curve(curve_today, curve_prior_year, save_path):
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    _apply_style(ax, fig)

    tenors_today = sorted(curve_today.keys())
    ax.plot(tenors_today, [curve_today[t] for t in tenors_today],
            color=DIVERGING_POSITIVE, lw=2.4, marker="o", markersize=5,
            label="Today")

    if curve_prior_year:
        tenors_prior = sorted(curve_prior_year.keys())
        ax.plot(tenors_prior, [curve_prior_year[t] for t in tenors_prior],
                color=INK_MUTED, lw=1.6, ls="--", marker="o", markersize=4,
                label="~1 year ago")

    ax.set_xscale("log")
    ax.set_xticks(sorted(set(TENORS.values())))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v*12:.0f}m" if v < 1 else f"{v:.0f}y"))
    ax.set_xlabel("Maturity")
    ax.set_ylabel("Par yield (%)")
    ax.set_title("U.S. Treasury Par Yield Curve (source: FRED)",
                 fontsize=12, weight="bold", loc="left")
    ax.legend(fontsize=8.5, frameon=False, labelcolor=INK_SECONDARY)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_yield_vs_vol(df, save_path):
    fig, ax = plt.subplots(figsize=(9.5, 7))
    _apply_style(ax, fig)

    for family in FAMILY_ORDER:
        group = df[df["family"] == family]
        if group.empty:
            continue
        ax.scatter(group["current_vol_pct"], group["current_yield_pct"],
                  s=95, alpha=0.85, label=family,
                  color=FAMILY_COLORS[family], edgecolor="white", linewidth=0.6)
        for _, row in group.iterrows():
            ax.annotate(row["ticker"], (row["current_vol_pct"], row["current_yield_pct"]),
                       fontsize=7, color=INK_SECONDARY,
                       xytext=(4, 4), textcoords="offset points")

    ax.set_xlabel("Realized annualized volatility (%)")
    ax.set_ylabel("Current trailing-12m yield (%)")
    ax.set_title("Fixed Income Universe — Yield vs. Risk (live data)",
                 fontsize=12, weight="bold", loc="left")
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=4, frameon=False, labelcolor=INK_SECONDARY)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_spread_to_treasury(df, save_path):
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    _apply_style(ax, fig)

    sorted_df = df.sort_values("spread_to_treasury_bps")
    colors = [DIVERGING_POSITIVE if v > 0 else DIVERGING_NEGATIVE
              for v in sorted_df["spread_to_treasury_bps"]]

    ax.barh(sorted_df["ticker"], sorted_df["spread_to_treasury_bps"], color=colors, height=0.7)
    ax.axvline(0, color=INK_PRIMARY, lw=1.0)
    ax.set_xlabel("Spread to duration-matched Treasury yield (bps)\n"
                 "(>0 = yielding more than a same-duration Treasury, potentially cheap  |  "
                 "<0 = yielding less, potentially rich)")
    ax.set_title("Relative Value vs. the Live Treasury Curve — by Fund",
                 fontsize=12, weight="bold", loc="left")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_yield_percentile(df, save_path):
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    _apply_style(ax, fig)

    sorted_df = df.sort_values("yield_percentile_vs_own_history")
    colors = [DIVERGING_POSITIVE if v > 50 else DIVERGING_NEGATIVE
              for v in sorted_df["yield_percentile_vs_own_history"]]

    ax.barh(sorted_df["ticker"], sorted_df["yield_percentile_vs_own_history"], color=colors, height=0.7)
    ax.axvline(50, color=INK_PRIMARY, lw=1.0, ls="--")
    ax.set_xlabel("Current yield percentile vs. own trailing history\n"
                 "(>50 = yielding more than usual, potentially cheap  |  <50 = yielding less than usual, potentially rich)")
    ax.set_title("Current Yield vs. Own History — by Fund", fontsize=12, weight="bold", loc="left")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)
