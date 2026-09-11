# Power BI Build Guide — Healthcare / Pharma Analytics Dashboard

A page-by-page guide to assembling the interactive .pbix from
`data/pharma_prescribing_simulated.csv`. Budget ~45-60 minutes.

**Before you start:** follow `Data_Model_Notes.md` to import the tables, build
the Date table, and mark it as the model's date table. Then paste every
measure from `DAX_Measures.md`.

---

## Page 1 — Executive Summary

**Purpose:** the page a VP opens first — top-line KPIs and the headline
finding (Ohio underperforming, Ozempic/Mounjaro surging).

1. **KPI cards** (Card visual) across the top: `[Total Prescriptions]`,
   `[Total Revenue]`, `[Distinct Doctors]`, `[Distinct Molecules]`.
2. **Line chart**: X = `Date[MonthName]`, Y = `[Total Prescriptions]`. This
   is the overall trend — should match Excel's "Overall Monthly Prescribing
   Trend" chart exactly.
3. **Text box**: "⚠ SIMULATED DATA — see README.md" in the top-right corner,
   small but visible on every page (copy this visual to every subsequent
   page via Ctrl+C / Ctrl+V, or set it in the page's background/theme).
4. **Callout visuals** (two side by side): one showing the flagged
   underperforming state (`States[state]` filtered to the underperformer,
   with `[Region Gap vs Portfolio %]` as the callout value), one showing the
   fastest-growing molecule (`[Prescriptions YoY %]` filtered to the top
   grower).

## Page 2 — Molecule & Therapy Uptake

**Purpose:** doctor-wise/molecule-wise performance and the growth vs.
decline story.

1. **Line chart**: X = `Date[MonthName]`, Y = `[Total Prescriptions]`, Legend
   = `Data[brand]`. Filter to 5-6 brands (3 growers, 3 decliners — e.g.
   Ozempic, Mounjaro, Jardiance vs. Humira, Imbruvica, Januvia) so the lines
   are readable; this reproduces the Excel "Therapy Uptake" chart.
2. **Table or matrix**: Rows = `Data[brand]`, `Data[therapy_area]`; Values =
   `[Total Prescriptions]`, `[Total Revenue]`, `[Prescriptions YoY %]`.
   Apply conditional formatting (background color scale) on the YoY %
   column — green for positive, red for negative.
3. **Slicer**: `Data[therapy_area]` (dropdown or list) to filter the whole
   page by therapy area.
4. **Bar chart**: Y = `Data[therapy_area]`, X = `[Total Revenue]` — revenue
   by therapy area.

## Page 3 — Regional Performance

**Purpose:** region-wise performance and the underperforming-region flag —
directly supports the marketing-budget-allocation narrative.

1. **Map visual** (or filled map): Location = `Data[state]`, Size =
   `[Total Revenue]`, Color saturation = `[Rx per Doctor (State)]`. If a
   map visual isn't available/licensed, substitute a bar chart.
2. **Bar chart**: Y = `Data[state]` sorted by `[Rx per Doctor (State)]`
   ascending, X = `[Rx per Doctor (State)]`. Add a constant reference line
   at the portfolio average (Format → Analytics → Average line, or a
   measure-based line using `[Portfolio Avg Rx per Doctor]`).
3. **Table**: Rows = `Data[state]`, Values = `[Total Prescriptions]`,
   `[Total Revenue]`, `[Distinct Doctors]`, `[Rx per Doctor (State)]`,
   `[Underperforming Region Flag]`. Conditional-format the flag column
   (red font for "⚠ Underperforming").
4. **Card**: `[Region Gap vs Portfolio %]` filtered to the flagged state,
   as a callout.

## Page 4 — Doctor Performance

**Purpose:** doctor-wise ranking, the third pillar the resume line names
explicitly.

1. **Table or bar chart**: Top 15-25 doctors by `[Total Revenue]`
   (`Data[doctor_name]`, `Data[specialty]`, `Data[state]`, `[Total
   Prescriptions]`, `[Total Revenue]`). Use `[Top 10 Doctor Flag]` for
   conditional formatting or a "Top 10" badge.
2. **Donut chart**: `Data[specialty]` by `[Total Revenue]` — revenue mix by
   specialty.
3. **Slicer**: `Data[specialty]` to filter the doctor table by specialty.

## Page 5 — Marketing Budget Reallocation

**Purpose:** the business-decision output — translates the underperforming-
region finding into a quantified budget proposal.

1. Import `outputs/budget_reallocation.csv` as its own table
   (`BudgetReallocation`) — it's a 10-row state-level summary, not part of
   the main fact table.
2. **Clustered bar chart**: Y = `BudgetReallocation[state]`, Values =
   `BudgetReallocation[current_budget]` and `BudgetReallocation[proposed_budget]`
   side by side.
3. **Card row**: Ohio's current budget, proposed budget, and the projected
   incremental revenue (`outputs/budget_impact_projection.json` — enter
   these three numbers as static cards, since they're a one-off scenario
   output, not something recomputed live from the fact table).
4. **Text box**: state the reallocation assumption plainly (15% of every
   other state's budget redirected to the flagged region; see the business
   report Section 9 for the full methodology) — a reader should never see a
   number on this page without knowing it's a planning assumption, not a
   measured result.

---

## Publishing

If you have a Power BI Service workspace (even a free one), **File →
Publish** after building the report, then paste the live share link at the
top of your README. A working, browsable link is worth far more to a
recruiter than a `.pbix` file they'd need to download and open in Desktop —
prioritize this over any other polish if you're short on time.

## Sanity check against the Excel workbook

Once built, `[Total Prescriptions]` on Page 1 should read **145,856** and
`[Total Revenue]` should read **$205,905,423** (rounded) — identical to the
Excel Dashboard sheet, since both read the same source CSV. If these don't
match, revisit the data-type check in `Data_Model_Notes.md` before anything
else.
