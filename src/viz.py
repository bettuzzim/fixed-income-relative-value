"""
viz.py
-------
Two charts:
  1. Bubble chart of current yield vs. volatility, one point per ETF,
     colored by broad segment family — visualizes where the "best
     compensation per unit of risk" currently sits across the fixed-income
     universe.
  2. Horizontal bar chart of each ETF's current yield percentile versus
     its own trailing history — how rich/cheap each segment looks
     relative to itself, not to an external assumption.
"""

import matplotlib.pyplot as plt

FAMILY_COLORS = {
    "US Treasury": "#1a2b4a",
    "TIPS": "#2f5c8a",
    "IG Corporate": "#4a7c59",
    "HY Corporate": "#8b2e2e",
    "Bank Loans": "#b3862f",
    "EM Debt": "#c9772e",
    "International": "#5c1a5c",
    "Aggregate": "#555555",
    "Municipal": "#3a7a7a",
}


def _family(segment_label):
    for key in FAMILY_COLORS:
        if key.split()[0].lower() in segment_label.lower():
            return key
    return "Other"


def plot_yield_vs_vol(df, save_path):
    fig, ax = plt.subplots(figsize=(8.5, 6.5))

    df = df.copy()
    df["family"] = df["segment"].apply(_family)

    for family, group in df.groupby("family"):
        ax.scatter(group["current_vol_pct"], group["current_yield_pct"],
                  s=90, alpha=0.8, label=family,
                  color=FAMILY_COLORS.get(family, "#999999"), edgecolor="white")
        for _, row in group.iterrows():
            ax.annotate(row["ticker"], (row["current_vol_pct"], row["current_yield_pct"]),
                       fontsize=7, xytext=(4, 4), textcoords="offset points")

    ax.set_xlabel("Realized annualized volatility (%)")
    ax.set_ylabel("Current trailing-12m yield (%)")
    ax.set_title("Fixed Income Universe — Yield vs. Risk (live data)",
                 fontsize=11, weight="bold")
    ax.legend(fontsize=7.5, loc="upper left", ncol=2)
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_yield_percentile(df, save_path):
    fig, ax = plt.subplots(figsize=(8, 7))

    sorted_df = df.sort_values("yield_percentile_vs_own_history")
    colors = ["#4a7c59" if v > 50 else "#8b2e2e" for v in sorted_df["yield_percentile_vs_own_history"]]

    ax.barh(sorted_df["ticker"], sorted_df["yield_percentile_vs_own_history"], color=colors)
    ax.axvline(50, color="black", lw=0.8, ls="--")
    ax.set_xlabel("Current yield percentile vs. own trailing history\n"
                 "(>50 = yielding more than usual, potentially cheap  |  <50 = yielding less than usual, potentially rich)")
    ax.set_title("Current Yield vs. Own History — by ETF", fontsize=11, weight="bold")
    ax.grid(alpha=0.25, axis="x")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
