"""
Healthcare / Pharma Analytics Dashboard — SIMULATED DATA GENERATOR
======================================================================
IMPORTANT: This dataset is SIMULATED, not real patient/prescriber data.

Why simulated: the only genuinely real public dataset with this exact
shape (doctor-wise, drug-wise, region-wise prescription volume) is CMS's
Medicare Part D Prescribers by Provider and Drug dataset. That real
dataset is 25M+ rows / several GB, hosted only on data.cms.gov (which
this environment cannot bulk-download), and would in any case need
heavy filtering before it were usable in Excel or a BI tool. Rather
than fabricate a small "real-looking" excerpt, this generator builds a
transparent, clearly-labeled synthetic dataset — sized for a BI
dashboard — but calibrated to real, cited, current facts about the
Medicare Part D program so the patterns it contains are realistic:

  - The 16 drugs used are real, currently-marketed drugs, chosen from
    the actual top-spending Part D drug list (source: CMS Medicare Part
    D Spending by Drug Dashboard via KFF/AARP/Visual Capitalist
    reporting, 2021-2024). See README.md for the full citation list.
  - Growth/decline trajectories follow real, publicly reported directional
    trends for each drug (e.g., Ozempic/Mounjaro's well-documented 2022-2024
    growth surge; Humira's well-documented 2023 biosimilar-driven decline).
  - No real patient, physician, or NPI data is used anywhere. Doctor
    names/IDs, exact prescription counts, and exact dollar figures are
    entirely synthetic.

Run: python3 01_generate_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RNG = np.random.default_rng(42)

# ----------------------------------------------------------------------
# Real drugs, grouped into real therapy areas, each with a stated,
# cited real-world 2022-2024 directional trend and an illustrative
# (not exact WAC/list-price) approximate monthly cost per prescription.
# ----------------------------------------------------------------------
MOLECULES = [
    # (molecule, brand, therapy_area, base_monthly_rx_per_doctor, trend_pct_per_month, approx_cost_per_rx)
    ("Semaglutide",     "Ozempic",   "Diabetes & Metabolic", 14, 0.028, 950),
    ("Tirzepatide",     "Mounjaro",  "Diabetes & Metabolic",  6, 0.045, 1050),
    ("Empagliflozin",   "Jardiance", "Diabetes & Metabolic", 11, 0.014, 550),
    ("Dulaglutide",     "Trulicity", "Diabetes & Metabolic", 10, 0.004, 900),
    ("Dapagliflozin",   "Farxiga",   "Diabetes & Metabolic",  8, 0.010, 560),
    ("Sitagliptin",     "Januvia",   "Diabetes & Metabolic",  9, -0.012, 540),
    ("Apixaban",        "Eliquis",   "Cardiovascular",       16, 0.006, 480),
    ("Rivaroxaban",     "Xarelto",   "Cardiovascular",       12, 0.003, 470),
    ("Sacubitril-Valsartan", "Entresto", "Cardiovascular",    7, 0.020, 610),
    ("Adalimumab",      "Humira",    "Immunology",            9, -0.028, 6800),
    ("Etanercept",      "Enbrel",    "Immunology",            6, -0.010, 6200),
    ("Ustekinumab",     "Stelara",   "Immunology",            5, -0.004, 7400),
    ("Ibrutinib",       "Imbruvica", "Oncology",               4, -0.016, 15200),
    ("Palbociclib",     "Ibrance",   "Oncology",               5, 0.005, 14600),
    ("Fluticasone-Umeclidinium-Vilanterol", "Trelegy Ellipta", "Respiratory", 10, 0.017, 420),
    ("Bictegravir-Emtricitabine-Tenofovir", "Biktarvy", "Infectious Disease (HIV)", 8, 0.019, 3750),
]
mol_df = pd.DataFrame(MOLECULES, columns=[
    "molecule", "brand", "therapy_area", "base_rx", "monthly_trend", "approx_cost_per_rx"
])

# ----------------------------------------------------------------------
# Real US states, grouped into real US Census regions. One state is
# deliberately given a sustained negative performance multiplier and
# one a modest positive multiplier, to produce a genuine, discoverable
# "underperforming region" finding (real regional variation in market
# access, formulary coverage, and sales-rep coverage is well documented
# in the pharma commercial literature; the specific multipliers here
# are illustrative, not measured).
# ----------------------------------------------------------------------
STATES = [
    # (state, census_region, performance_multiplier)
    ("California", "West", 1.05),
    ("Texas", "South", 0.97),
    ("New York", "Northeast", 1.10),
    ("Florida", "South", 0.95),
    ("Illinois", "Midwest", 1.00),
    ("Pennsylvania", "Northeast", 0.98),
    ("Ohio", "Midwest", 0.78),      # deliberately underperforming
    ("Georgia", "South", 0.99),
    ("North Carolina", "South", 1.02),
    ("Arizona", "West", 1.15),      # deliberately strong performer
]
state_df = pd.DataFrame(STATES, columns=["state", "region", "perf_multiplier"])

# ----------------------------------------------------------------------
# Specialties, each linked to the therapy area(s) they prescribe in —
# a realistic prescribing-pattern constraint (an oncologist does not
# prescribe HIV antiretrovirals, etc.)
# ----------------------------------------------------------------------
SPECIALTIES = {
    "Primary Care / Internal Medicine": ["Diabetes & Metabolic", "Cardiovascular"],
    "Endocrinology": ["Diabetes & Metabolic"],
    "Cardiology": ["Cardiovascular"],
    "Rheumatology": ["Immunology"],
    "Oncology": ["Oncology"],
    "Pulmonology": ["Respiratory"],
    "Infectious Disease": ["Infectious Disease (HIV)"],
}
N_DOCTORS_BY_SPECIALTY = {
    "Primary Care / Internal Medicine": 15, "Endocrinology": 12, "Cardiology": 12,
    "Rheumatology": 12, "Oncology": 12, "Pulmonology": 10, "Infectious Disease": 10,
}

FIRST_NAMES = ["James","Maria","Robert","Linda","David","Susan","Michael","Patricia","John","Jennifer",
               "William","Elizabeth","Richard","Barbara","Joseph","Nancy","Thomas","Karen","Charles","Betty",
               "Daniel","Sandra","Matthew","Ashley","Mark","Kimberly","Paul","Emily","Steven","Donna",
               "Andrew","Michelle","Kenneth","Carol","George","Amanda","Edward","Melissa","Brian","Deborah",
               "Anthony","Stephanie","Ronald","Rebecca","Kevin","Sharon","Jason","Laura","Jeffrey","Cynthia",
               "Ryan","Kathleen","Jacob","Amy","Gary","Angela","Nicholas","Shirley","Eric","Anna",
               "Jonathan","Brenda","Larry","Pamela","Justin","Emma","Scott","Nicole","Brandon","Helen",
               "Frank","Samantha","Benjamin","Katherine","Gregory","Christine","Raymond","Debra","Samuel","Rachel",
               "Patrick","Catherine","Alexander","Carolyn","Jack","Janet","Dennis","Ruth","Jerry","Diane"]
LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
              "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
              "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
              "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
              "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
              "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
              "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
              "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
              "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes"]

doctors = []
doc_id = 1
for specialty, n in N_DOCTORS_BY_SPECIALTY.items():
    for _ in range(n):
        state_row = state_df.sample(1, random_state=RNG.integers(0, 1_000_000)).iloc[0]
        fname = FIRST_NAMES[RNG.integers(0, len(FIRST_NAMES))]
        lname = LAST_NAMES[RNG.integers(0, len(LAST_NAMES))]
        doctors.append({
            "doctor_id": f"DR{doc_id:04d}",
            "doctor_name": f"Dr. {fname} {lname}",   # synthetic name, not a real physician
            "specialty": specialty,
            "state": state_row["state"],
            "region": state_row["region"],
        })
        doc_id += 1
doc_df = pd.DataFrame(doctors)

# ----------------------------------------------------------------------
# Build the monthly doctor x molecule panel, Jan 2022 - Dec 2024 (36 months)
# ----------------------------------------------------------------------
months = pd.date_range("2022-01-01", "2024-12-01", freq="MS")
rows = []
for _, doc in doc_df.iterrows():
    eligible_areas = SPECIALTIES[doc["specialty"]]
    eligible_molecules = mol_df[mol_df["therapy_area"].isin(eligible_areas)]
    perf_mult = state_df.loc[state_df["state"] == doc["state"], "perf_multiplier"].iloc[0]
    # each doctor has a personal baseline multiplier (some prescribe more than others)
    doc_mult = RNG.lognormal(mean=0.0, sigma=0.30)

    for _, mol in eligible_molecules.iterrows():
        for m_idx, month in enumerate(months):
            trend_factor = (1 + mol["monthly_trend"]) ** m_idx
            seasonal = 1 + 0.05 * np.sin(2 * np.pi * month.month / 12)
            expected_rx = mol["base_rx"] * trend_factor * seasonal * perf_mult * doc_mult
            expected_rx = max(expected_rx, 0.3)
            prescriptions = RNG.poisson(expected_rx)
            if prescriptions == 0 and RNG.random() > 0.15:
                continue  # most true-zero months are simply not recorded (no activity that month)
            unique_patients = max(1, int(round(prescriptions * RNG.uniform(0.55, 0.85)))) if prescriptions > 0 else 0
            cost_noise = RNG.uniform(0.92, 1.08)
            total_cost = round(prescriptions * mol["approx_cost_per_rx"] * cost_noise, 2)

            rows.append({
                "month": month.strftime("%Y-%m-01"),
                "doctor_id": doc["doctor_id"],
                "doctor_name": doc["doctor_name"],
                "specialty": doc["specialty"],
                "state": doc["state"],
                "region": doc["region"],
                "molecule": mol["molecule"],
                "brand": mol["brand"],
                "therapy_area": mol["therapy_area"],
                "prescriptions": int(prescriptions),
                "unique_patients": int(unique_patients),
                "total_cost": total_cost,
            })

df = pd.DataFrame(rows)
df.to_csv(DATA_DIR / "pharma_prescribing_simulated.csv", index=False)

print(f"SIMULATED dataset generated: {len(df):,} rows")
print(f"Doctors: {doc_df['doctor_id'].nunique()} | Molecules: {mol_df['molecule'].nunique()} | "
      f"States: {state_df['state'].nunique()} | Months: {len(months)}")
print(f"Total simulated prescriptions: {df['prescriptions'].sum():,}")
print(f"Total simulated cost: ${df['total_cost'].sum():,.0f}")

doc_df.to_csv(DATA_DIR / "doctors_reference.csv", index=False)
mol_df.to_csv(DATA_DIR / "molecules_reference.csv", index=False)
state_df.to_csv(DATA_DIR / "states_reference.csv", index=False)
