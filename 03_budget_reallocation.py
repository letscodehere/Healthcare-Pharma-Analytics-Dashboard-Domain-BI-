"""
Healthcare / Pharma Analytics Dashboard — Marketing Budget Reallocation
============================================================================
Translates the underperforming-region and therapy-uptake findings into a
concrete, quantified marketing-budget reallocation proposal — the
business-decision output the resume line calls for ("enabling data-driven
allocation of marketing budgets").

All dollar figures here are illustrative planning assumptions layered on
top of the SIMULATED prescribing data — clearly stated as such, exactly
like the LGD/loan-size/holding-cost assumptions in the earlier projects
in this series.

Run: python3 03_budget_reallocation.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "outputs"
ASSETS = BASE_DIR / "assets"

NAVY, TEAL, GOLD, RED, GREY = "#1F3864", "#2E8B8B", "#D4A017", "#B23A48", "#8C96A0"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.edgecolor": "#D9D9D9", "axes.grid": True,
    "grid.color": "#E8E8E8", "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
})

state_perf = pd.read_csv(f"{OUT_DIR}/state_performance.csv")
mol_perf = pd.read_csv(f"{OUT_DIR}/molecule_performance.csv")
with open(f"{OUT_DIR}/underperforming_region.json") as f:
    underperf = json.load(f)

# ----------------------------------------------------------------------
# STATED ILLUSTRATIVE ASSUMPTION: an annual field-marketing budget of
# $2,000,000 allocated across the 10 states in proportion to current
# revenue (the "status quo" allocation most commercial teams start
# from), with a proposed reallocation that shifts a modest share away
# from the lowest-growth molecules' states toward the flagged
# underperforming region (Ohio) and the fastest-growing therapy area.
# ----------------------------------------------------------------------
TOTAL_ANNUAL_BUDGET = 2_000_000
REALLOCATION_PCT = 0.15  # share of budget subject to reallocation, stated assumption

state_perf["current_budget_share"] = state_perf["total_revenue"] / state_perf["total_revenue"].sum()
state_perf["current_budget"] = (state_perf["current_budget_share"] * TOTAL_ANNUAL_BUDGET).round(0)

# Proposed: pull REALLOCATION_PCT of budget proportionally from the top
# revenue states (which are already over-performing and likely near
# saturation) and redirect it to Ohio, in proportion to the gap
# between Ohio's current rx/doctor and the portfolio average.
ohio_mask = state_perf["state"] == underperf["flagged_state"]
pool = (state_perf.loc[~ohio_mask, "current_budget"] * REALLOCATION_PCT).sum()
state_perf["proposed_budget"] = state_perf["current_budget"]
state_perf.loc[~ohio_mask, "proposed_budget"] = (state_perf.loc[~ohio_mask, "current_budget"] * (1 - REALLOCATION_PCT)).round(0)
state_perf.loc[ohio_mask, "proposed_budget"] = (state_perf.loc[ohio_mask, "current_budget"] + pool).round(0)
state_perf["budget_change"] = state_perf["proposed_budget"] - state_perf["current_budget"]
state_perf["budget_change_pct"] = (state_perf["budget_change"] / state_perf["current_budget"] * 100).round(1)
state_perf.to_csv(f"{OUT_DIR}/budget_reallocation.csv", index=False)

ohio_new_budget = state_perf.loc[ohio_mask, "proposed_budget"].iloc[0]
ohio_old_budget = state_perf.loc[ohio_mask, "current_budget"].iloc[0]
print(f"Ohio budget: ${ohio_old_budget:,.0f} -> ${ohio_new_budget:,.0f} "
      f"(+{(ohio_new_budget-ohio_old_budget)/ohio_old_budget*100:.0f}%)")
print(state_perf[["state", "current_budget", "proposed_budget", "budget_change_pct"]].to_string(index=False))

# ----------------------------------------------------------------------
# Projected impact: IF the additional Ohio investment closes HALF of the
# current gap to the portfolio average (a stated, conservative planning
# assumption — not a guaranteed or measured result), estimate the
# resulting incremental prescriptions and revenue.
# ----------------------------------------------------------------------
GAP_CLOSURE_ASSUMPTION = 0.50
ohio_row = state_perf.loc[ohio_mask].iloc[0]
target_rx_per_doctor = ohio_row["rx_per_doctor"] + GAP_CLOSURE_ASSUMPTION * (
    underperf["portfolio_avg_rx_per_doctor"] - ohio_row["rx_per_doctor"]
)
incremental_rx = (target_rx_per_doctor - ohio_row["rx_per_doctor"]) * ohio_row["doctors"]
avg_revenue_per_rx = state_perf["total_revenue"].sum() / state_perf["total_rx"].sum()
incremental_revenue = incremental_rx * avg_revenue_per_rx

impact_summary = {
    "reallocation_pct_of_non_ohio_budget": REALLOCATION_PCT * 100,
    "ohio_budget_before": float(ohio_old_budget),
    "ohio_budget_after": float(ohio_new_budget),
    "ohio_budget_increase_pct": round(float((ohio_new_budget - ohio_old_budget) / ohio_old_budget * 100), 1),
    "gap_closure_assumption_pct": GAP_CLOSURE_ASSUMPTION * 100,
    "projected_incremental_rx_per_year": round(float(incremental_rx), 0),
    "projected_incremental_revenue_per_year": round(float(incremental_revenue), 0),
}
with open(f"{OUT_DIR}/budget_impact_projection.json", "w") as f:
    json.dump(impact_summary, f, indent=2)
print("\nProjected impact:\n", json.dumps(impact_summary, indent=2))

# Chart: current vs proposed budget by state
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(state_perf))
width = 0.35
order = state_perf.sort_values("current_budget", ascending=False)
ax.bar(x - width/2, order["current_budget"] / 1e3, width, label="Current Budget", color=GREY)
ax.bar(x + width/2, order["proposed_budget"] / 1e3, width, label="Proposed Budget", color=TEAL)
ax.set_xticks(x)
ax.set_xticklabels(order["state"], rotation=30, ha="right")
ax.set_ylabel("Annual Marketing Budget ($K, illustrative)")
ax.set_title(f"Proposed Marketing Budget Reallocation\n"
             f"({REALLOCATION_PCT*100:.0f}% of non-Ohio budget redirected to the underperforming region)",
             fontsize=12, fontweight="bold", color=NAVY, loc="left")
ax.legend()
fig.tight_layout()
fig.savefig(f"{ASSETS}/07_budget_reallocation.png", dpi=160)
plt.close(fig)

print("\nBudget reallocation analysis complete.")
