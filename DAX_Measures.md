# DAX Measures — Healthcare / Pharma Analytics Dashboard

Paste these into Power BI Desktop as new measures on the `Data` table (or a
dedicated measures table — recommended: create one blank table named
`_Measures` via Modeling → New Table → `_Measures = ROW("x", 0)`, then move
every measure below onto it via the Properties pane, so measures aren't
scattered across the Data table).

**Reminder: the underlying data is SIMULATED** (see README.md and the Read Me
sheet in the Excel workbook) — these measures are correct and reusable
against real prescriber data, but the numbers they currently return are not
real prescriptions or real revenue.

## 1. Core KPIs

```dax
Total Prescriptions = SUM(Data[prescriptions])

Total Revenue = SUM(Data[total_cost])

Total Unique Patient-Instances = SUM(Data[unique_patients])

Distinct Doctors = DISTINCTCOUNT(Data[doctor_id])

Distinct Molecules = DISTINCTCOUNT(Data[molecule])

Avg Order Value =
DIVIDE([Total Revenue], [Total Prescriptions], 0)

Avg Prescriptions per Doctor =
DIVIDE([Total Prescriptions], [Distinct Doctors], 0)

Avg Revenue per Doctor =
DIVIDE([Total Revenue], [Distinct Doctors], 0)
```

## 2. Time Intelligence & Therapy Uptake

Requires a proper Date table (see `Data_Model_Notes.md`) marked as the
model's date table and related to `Data[month]`.

```dax
Prescriptions LY =
CALCULATE([Total Prescriptions], SAMEPERIODLASTYEAR('Date'[Date]))

Prescriptions YoY % =
DIVIDE([Total Prescriptions] - [Prescriptions LY], [Prescriptions LY])

Rolling 6-Month Avg Prescriptions =
AVERAGEX(
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -6, MONTH),
    [Total Prescriptions]
)

-- First-6-month vs last-6-month growth, used for the molecule
-- "growing / declining" classification (mirrors the Python calc in
-- notebooks/02_analysis.py, so Power BI and Excel agree)
First 6mo Avg Rx =
CALCULATE(
    AVERAGEX(VALUES('Date'[MonthYear]), [Total Prescriptions]),
    FILTER(ALL('Date'), 'Date'[Date] <= MIN('Date'[Date]) + 180)
)

Growth Flag =
VAR GrowthPct = [Prescriptions YoY %]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(GrowthPct), "No prior-year data",
        GrowthPct > 0.05, "🟢 Growing",
        GrowthPct < -0.05, "🔴 Declining",
        "🟡 Stable"
    )
```

## 3. Regional Analysis & Underperformer Flag

```dax
Rx per Doctor (State) =
DIVIDE([Total Prescriptions], [Distinct Doctors])

Portfolio Avg Rx per Doctor =
CALCULATE([Rx per Doctor (State)], ALL(Data[state]))

Region Gap vs Portfolio % =
DIVIDE([Rx per Doctor (State)] - [Portfolio Avg Rx per Doctor], [Portfolio Avg Rx per Doctor])

Underperforming Region Flag =
IF([Region Gap vs Portfolio %] < -0.25, "⚠ Underperforming", "On track")
```

Use `Underperforming Region Flag` as a conditional-formatting field (Format →
Conditional formatting → Font color) on any state-level table or map visual —
red for "⚠ Underperforming", green otherwise.

## 4. Doctor & Specialty Analysis

```dax
Doctor Rank by Revenue =
RANKX(ALL(Data[doctor_id]), [Total Revenue], , DESC)

Top 10 Doctor Flag =
IF([Doctor Rank by Revenue] <= 10, "Top 10", "Other")

Specialty Revenue Share % =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(Data[specialty])))
```

## 5. Budget Reallocation Page

These reference a separate `BudgetReallocation` table (import
`outputs/budget_reallocation.csv` as its own Power BI table — it's a
state-level summary table, not part of the main `Data` fact table).

```dax
Budget Change $ = SUM(BudgetReallocation[budget_change])

Budget Change % =
DIVIDE(
    SUM(BudgetReallocation[proposed_budget]) - SUM(BudgetReallocation[current_budget]),
    SUM(BudgetReallocation[current_budget])
)
```

## Notes on matching the Excel workbook

Every measure above is designed to reproduce the exact same numbers as the
Excel workbook's live formulas and Python-precomputed tables — e.g.
`[Total Prescriptions]` should equal the Excel Dashboard sheet's cell B6
(145,856 in the current simulated dataset) once you've loaded
`data/pharma_prescribing_simulated.csv` unmodified. If your numbers don't
match, check that Power Query hasn't silently changed a data type (a common
cause — see `Data_Model_Notes.md`).
