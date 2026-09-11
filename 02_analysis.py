"""
Healthcare / Pharma Analytics Dashboard — Core Analysis
===========================================================
Reads the SIMULATED dataset (see 01_generate_data.py and the README's
data-labeling notice) and produces every KPI, breakdown, and chart used
in the Excel dashboard, Power BI build guide, and business report.

Run: python3 02_analysis.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "outputs"
ASSETS = BASE_DIR / "assets"
for d in (OUT_DIR, ASSETS):
    d.mkdir(exist_ok=True)

NAVY, TEAL, GOLD, RED, GREY = "#1F3864", "#2E8B8B", "#D4A017", "#B23A48", "#8C96A0"
PALETTE = [NAVY, TEAL, GOLD, RED, "#7FB3B0", "#5B7DB1"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.edgecolor": "#D9D9D9", "axes.grid": True,
    "grid.color": "#E8E8E8", "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white",
})

df = pd.read_csv(DATA_DIR / "pharma_prescribing_simulated.csv", parse_dates=["month"])
print(f"Loaded {len(df):,} SIMULATED rows | {df['doctor_id'].nunique()} doctors | "
      f"{df['molecule'].nunique()} molecules | {df['state'].nunique()} states")

# ----------------------------------------------------------------------
# 1. Top-line KPIs
# ----------------------------------------------------------------------
kpi = {
    "Total Prescriptions": int(df["prescriptions"].sum()),
    "Total Unique Patient-Instances": int(df["unique_patients"].sum()),
    "Total Revenue (simulated)": round(df["total_cost"].sum(), 2),
    "Doctors": int(df["doctor_id"].nunique()),
    "Molecules Tracked": int(df["molecule"].nunique()),
    "Therapy Areas": int(df["therapy_area"].nunique()),
    "States Covered": int(df["state"].nunique()),
    "Date Range": f"{df['month'].min().strftime('%b %Y')} to {df['month'].max().strftime('%b %Y')}",
}
pd.Series(kpi).to_csv(OUT_DIR / "kpi_summary.csv")
print("\nKPIs:", kpi)

# ----------------------------------------------------------------------
# 2. Molecule-wise performance + therapy uptake trend
# ----------------------------------------------------------------------
mol_perf = df.groupby(["molecule", "brand", "therapy_area"]).agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum")
).reset_index().sort_values("total_revenue", ascending=False)

# growth rate: first-6-months avg vs last-6-months avg, monthly total across all doctors
mol_monthly = df.groupby(["brand", "month"])["prescriptions"].sum().reset_index()
growth_rows = []
for brand in mol_monthly["brand"].unique():
    s = mol_monthly[mol_monthly["brand"] == brand].sort_values("month")
    first6 = s["prescriptions"].iloc[:6].mean()
    last6 = s["prescriptions"].iloc[-6:].mean()
    growth_pct = (last6 - first6) / first6 * 100 if first6 > 0 else np.nan
    growth_rows.append({"brand": brand, "first_6mo_avg_rx": round(first6, 1),
                         "last_6mo_avg_rx": round(last6, 1), "growth_pct": round(growth_pct, 1)})
growth_df = pd.DataFrame(growth_rows).sort_values("growth_pct", ascending=False)
mol_perf = mol_perf.merge(growth_df, on="brand")
mol_perf.to_csv(OUT_DIR / "molecule_performance.csv", index=False)
print("\nMolecule performance (top 5 by revenue):\n", mol_perf.head(5).to_string(index=False))
print("\nFastest growing:\n", growth_df.head(3).to_string(index=False))
print("\nDeclining:\n", growth_df.tail(3).to_string(index=False))

# Therapy uptake trend chart — growers vs decliners
fig, ax = plt.subplots(figsize=(10, 5))
growers = ["Ozempic", "Mounjaro", "Jardiance"]
decliners = ["Humira", "Imbruvica", "Januvia"]
for brand, color in zip(growers, [NAVY, TEAL, GOLD]):
    s = mol_monthly[mol_monthly["brand"] == brand].sort_values("month")
    ax.plot(s["month"], s["prescriptions"], label=f"{brand} (growth)", color=color, linewidth=2.2)
for brand, color in zip(decliners, [RED, "#D88C97", "#8C96A0"]):
    s = mol_monthly[mol_monthly["brand"] == brand].sort_values("month")
    ax.plot(s["month"], s["prescriptions"], label=f"{brand} (decline)", color=color, linewidth=1.8, linestyle="--")
ax.set_title("Therapy Uptake: Growth vs. Decline Trends (simulated, 2022-2024)",
             fontsize=13, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("Monthly Prescriptions (all doctors)")
ax.legend(fontsize=9, ncol=2)
fig.tight_layout()
fig.savefig(ASSETS / "01_therapy_uptake_trend.png", dpi=160)
plt.close(fig)

# Revenue by therapy area
ta_perf = df.groupby("therapy_area").agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum")
).reset_index().sort_values("total_revenue", ascending=False)
ta_perf.to_csv(OUT_DIR / "therapy_area_performance.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(ta_perf["therapy_area"], ta_perf["total_revenue"] / 1e6, color=NAVY)
ax.set_ylabel("Total Revenue ($M, simulated)")
ax.set_title("Revenue by Therapy Area (simulated)", fontsize=13, fontweight="bold", color=NAVY, loc="left")
ax.tick_params(axis="x", rotation=20)
fig.tight_layout()
fig.savefig(ASSETS / "02_revenue_by_therapy_area.png", dpi=160)
plt.close(fig)

# ----------------------------------------------------------------------
# 3. Region-wise / state-wise performance + underperforming region flag
# ----------------------------------------------------------------------
state_perf = df.groupby("state").agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum"),
    doctors=("doctor_id", "nunique"),
).reset_index()
state_perf["rx_per_doctor"] = (state_perf["total_rx"] / state_perf["doctors"]).round(1)
state_perf["revenue_per_doctor"] = (state_perf["total_revenue"] / state_perf["doctors"]).round(0)
state_perf = state_perf.sort_values("rx_per_doctor")
state_perf.to_csv(OUT_DIR / "state_performance.csv", index=False)
print("\nState performance (rx per doctor, lowest first):\n", state_perf.to_string(index=False))

portfolio_avg_rx_per_doctor = (df["prescriptions"].sum() / df["doctor_id"].nunique())
underperformer = state_perf.iloc[0]
gap_pct = (portfolio_avg_rx_per_doctor - underperformer["rx_per_doctor"]) / portfolio_avg_rx_per_doctor * 100
implied_missed_rx = (portfolio_avg_rx_per_doctor - underperformer["rx_per_doctor"]) * underperformer["doctors"]
avg_revenue_per_rx = df["total_cost"].sum() / df["prescriptions"].sum()
implied_missed_revenue = implied_missed_rx * avg_revenue_per_rx

underperf_summary = {
    "flagged_state": underperformer["state"],
    "state_rx_per_doctor": underperformer["rx_per_doctor"],
    "portfolio_avg_rx_per_doctor": round(portfolio_avg_rx_per_doctor, 1),
    "gap_pct_below_average": round(gap_pct, 1),
    "implied_missed_rx_if_at_average": round(implied_missed_rx, 0),
    "implied_missed_revenue_if_at_average": round(implied_missed_revenue, 0),
}
import json
with open(OUT_DIR / "underperforming_region.json", "w") as f:
    json.dump(underperf_summary, f, indent=2)
print("\nUnderperforming region analysis:\n", json.dumps(underperf_summary, indent=2))

fig, ax = plt.subplots(figsize=(9, 5))
colors = [RED if s == underperformer["state"] else TEAL for s in state_perf["state"]]
ax.barh(state_perf["state"], state_perf["rx_per_doctor"], color=colors)
ax.axvline(portfolio_avg_rx_per_doctor, color=NAVY, linestyle="--", linewidth=1.5, label="Portfolio average")
ax.set_xlabel("Prescriptions per Doctor (2022-2024 total)")
ax.set_title("Prescribing Volume per Doctor by State\nUnderperforming Region Flagged",
             fontsize=12, fontweight="bold", color=NAVY, loc="left")
ax.legend()
fig.tight_layout()
fig.savefig(ASSETS / "03_state_performance.png", dpi=160)
plt.close(fig)

# Region (Census region) roll-up
region_perf = df.groupby("region").agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum"), doctors=("doctor_id", "nunique")
).reset_index().sort_values("total_revenue", ascending=False)
region_perf.to_csv(OUT_DIR / "region_performance.csv", index=False)

# ----------------------------------------------------------------------
# 4. Doctor-wise performance
# ----------------------------------------------------------------------
doc_perf = df.groupby(["doctor_id", "doctor_name", "specialty", "state"]).agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum")
).reset_index().sort_values("total_revenue", ascending=False)
doc_perf.to_csv(OUT_DIR / "doctor_performance.csv", index=False)
print("\nTop 10 doctors by revenue:\n", doc_perf.head(10)[["doctor_name", "specialty", "state", "total_rx", "total_revenue"]].to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5.5))
top15 = doc_perf.head(15).sort_values("total_revenue")
ax.barh(top15["doctor_name"], top15["total_revenue"] / 1e3, color=TEAL)
ax.set_xlabel("Total Revenue ($K, simulated)")
ax.set_title("Top 15 Doctors by Prescribing Revenue (simulated)", fontsize=12, fontweight="bold", color=NAVY, loc="left")
fig.tight_layout()
fig.savefig(ASSETS / "04_top_doctors.png", dpi=160)
plt.close(fig)

# Specialty roll-up
spec_perf = df.groupby("specialty").agg(
    total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum"), doctors=("doctor_id", "nunique")
).reset_index().sort_values("total_revenue", ascending=False)
spec_perf.to_csv(OUT_DIR / "specialty_performance.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(spec_perf["specialty"], spec_perf["total_revenue"] / 1e6, color=GOLD)
ax.set_ylabel("Total Revenue ($M, simulated)")
ax.set_title("Revenue by Specialty (simulated)", fontsize=12, fontweight="bold", color=NAVY, loc="left")
ax.tick_params(axis="x", rotation=25)
fig.tight_layout()
fig.savefig(ASSETS / "05_revenue_by_specialty.png", dpi=160)
plt.close(fig)

# ----------------------------------------------------------------------
# 5. Overall monthly trend
# ----------------------------------------------------------------------
monthly = df.groupby("month").agg(total_rx=("prescriptions", "sum"), total_revenue=("total_cost", "sum")).reset_index()
monthly.to_csv(OUT_DIR / "monthly_trend.csv", index=False)

fig, ax1 = plt.subplots(figsize=(10, 4.2))
ax1.plot(monthly["month"], monthly["total_rx"], color=NAVY, linewidth=2.2)
ax1.fill_between(monthly["month"], monthly["total_rx"], color=NAVY, alpha=0.08)
ax1.set_ylabel("Total Monthly Prescriptions")
ax1.set_title("Overall Prescribing Trend, 2022-2024 (simulated)", fontsize=13, fontweight="bold", color=NAVY, loc="left")
fig.tight_layout()
fig.savefig(ASSETS / "06_overall_trend.png", dpi=160)
plt.close(fig)

print("\nAnalysis complete. All outputs and charts written.")
