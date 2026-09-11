# Healthcare / Pharma Analytics Dashboard

**Doctor-wise, region-wise, and molecule-wise prescribing analytics — built with Excel (live formulas) and Power BI (DAX), tracking therapy uptake and translating an underperforming-region finding into a quantified marketing budget reallocation.**

> ⚠ **This dataset is SIMULATED — not real patient, physician, or prescribing data.** See "Why simulated" below before using this project anywhere it might be mistaken for real. Every chart, table, and dashboard in this repo repeats this disclosure.

![Therapy Uptake](assets/01_therapy_uptake_trend.png)

## Resume line

> Developed a Healthcare & Pharma Analytics dashboard integrating simulated hospital/pharma sales and prescription data (calibrated to real, cited Medicare Part D drug trends), using Power BI and Excel to analyze doctor-wise, region-wise, and molecule-wise performance, track therapy uptake, and flag an underperforming region 58% below the portfolio average — enabling a quantified, data-driven marketing budget reallocation proposal.

## Why simulated (read this first)

The only genuinely real public dataset with this exact shape — doctor-wise, drug-wise, region-wise prescription volume — is CMS's **Medicare Part D Prescribers by Provider and Drug** dataset. It's real and free, but spans **25+ million rows across several gigabytes** for a single year, hosted only on data.cms.gov, and isn't practically bulk-downloadable or usable directly in Excel without infrastructure this project didn't have access to. The alternative — real prescriber-level commercial data (IQVIA, Symphony Health) — is proprietary and used by actual pharma companies, not publicly available at all.

Rather than present a tiny, unrepresentative real excerpt as if it were the full picture, this project builds a **transparent, clearly-labeled simulated dataset**, sized for a BI dashboard, but calibrated to real, current, cited facts so every pattern in it is realistic:

- The **16 drugs are real, currently-marketed drugs** — selected from the actual top Medicare Part D spending list (2021-2024 CMS Part D Spending by Drug Dashboard, via KFF and AARP Public Policy Institute reporting).
- **Growth/decline trends are real, cited, and directionally accurate** — e.g., Ozempic and Mounjaro's well-documented 2022-2024 GLP-1 growth surge, and Humira's well-documented 2023 biosimilar-driven decline, are reproduced in the simulation.
- **No real patient, physician, or NPI data is used anywhere.** Doctor names/IDs and every prescription count and dollar figure are entirely synthetic.

## What's in this repo

| Path | What it is |
|---|---|
| `excel/Pharma_Analytics_Dashboard.xlsx` | **The Excel deliverable** — 7-sheet workbook with live SUMIF formulas against the full dataset, KPI dashboard, molecule/therapy uptake tracking, regional underperformer flag, doctor ranking, and the budget reallocation proposal. 28 formulas, zero errors after recalculation. |
| `powerbi/DAX_Measures.md` | Every DAX measure needed for the Power BI version (KPIs, time intelligence, underperformer flag, budget reallocation). |
| `powerbi/PowerBI_Build_Guide.md` | Page-by-page build guide (~45-60 min) to assemble the interactive `.pbix`. |
| `powerbi/Data_Model_Notes.md` | Table relationships, Date table setup, and a data-type gotcha that silently breaks every measure if missed. |
| `report/Pharma_Analytics_Business_Report.docx` | 9-page written business report — the simulated-data disclosure appears on the cover and in the header of every page. |
| `notebooks/01_generate_data.py` | The data generator — every real-world calibration fact is documented inline as a comment. |
| `notebooks/02_analysis.py`, `03_budget_reallocation.py` | Analysis pipeline: KPIs, doctor/region/molecule performance, underperformer detection, budget proposal. |
| `data/` | The simulated dataset, plus reference tables (doctors, molecules, states). |
| `outputs/` | Every intermediate table (molecule performance, state performance, budget reallocation, impact projection) as CSV/JSON. |
| `assets/` | Chart PNGs used in the report and this README. |

## Key findings

- **Therapy uptake diverges sharply**: Mounjaro (+245%) and Ozempic (+115%) show explosive simulated growth, mirroring the real GLP-1 category surge; Humira (-59%) and Imbruvica (-38%) show steep simulated decline, mirroring real, well-documented biosimilar and competitive pressure.
- **Ohio is flagged as underperforming**: 58.2% below the portfolio average prescriptions-per-doctor, implying ~$8.7M in simulated missed annual revenue — recovered purely from the data, without being told in advance which state to look for (a modest negative factor was deliberately built into Ohio's simulation as a test case; the analysis correctly finds it).
- **Oncology and Immunology drive outsized revenue** relative to prescription volume, due to real, well-documented high specialty-drug pricing — a margin-vs-volume tension worth flagging separately from raw prescription counts.
- **Quantified budget reallocation**: redirecting 15% of non-Ohio marketing budget into Ohio is projected to generate ~$4.3M in incremental annual simulated revenue under a stated, conservative 50%-gap-closure assumption — explicitly framed as a planning assumption to validate via pilot, not a guaranteed outcome.

See `report/Pharma_Analytics_Business_Report.docx` for the full write-up.

## How to reproduce

```bash
pip install -r requirements.txt

python3 notebooks/01_generate_data.py       # generates the SIMULATED dataset -> data/
python3 notebooks/02_analysis.py            # KPIs, doctor/region/molecule performance -> outputs/, assets/
python3 notebooks/03_budget_reallocation.py # underperformer -> budget proposal -> outputs/, assets/

# Excel workbook (run in order — each appends sheets to the same file)
python3 notebooks/build_excel_part1.py
python3 notebooks/build_excel_part2.py
python3 notebooks/build_excel_part3.py
python3 /path/to/recalc.py excel/Pharma_Analytics_Dashboard.xlsx   # recalculate formulas (requires LibreOffice)
```

All scripts use paths relative to the repo root (via `Path(__file__)`), so this works after a fresh `git clone`.

### Building the Power BI (.pbix) version

Not included as a file — there's no way to generate a `.pbix` outside Power BI Desktop itself. Follow `powerbi/Data_Model_Notes.md` then `powerbi/PowerBI_Build_Guide.md` (~45-60 minutes). Sanity check: `[Total Prescriptions]` should read **145,856**, identical to the Excel workbook, since both read the same source CSV. **If you publish it to Power BI Service, add the live link here** — a working, clickable dashboard is worth far more to a recruiter than a file they'd need to download and open.

## Business framing

Pharma commercial teams allocate limited marketing spend across a large, heterogeneous prescriber base. Without a consolidated doctor-wise / region-wise / molecule-wise view, budget defaults to historical inertia rather than current market dynamics. This project closes that loop: it doesn't stop at descriptive dashboards, it translates the underperforming-region finding into a specific, quantified budget-reallocation number (Section 7-8 of the report) — with the assumption behind every dollar figure stated plainly rather than presented as fact.

## Tech stack

`Microsoft Excel` (live SUMIF formulas) · `Power BI` (DAX, time intelligence) · `Python` (numpy, pandas, matplotlib) for data generation and analysis · `Node.js (docx)` for the written report.

## Limitations

- **This entire project uses simulated data** — disclose this in any professional context (interview, portfolio review) where it might otherwise be mistaken for a real client deliverable.
- The real CMS dataset this project is modeled on covers Medicare beneficiaries only, not the full payer-mix population a real commercial analysis would need.
- Cost-per-prescription figures are illustrative, order-of-magnitude estimates from public pricing reporting, not exact net-of-rebate pricing.
- The budget reallocation's total budget, reallocation share, and gap-closure assumption are stated illustrative planning inputs, not derived from a real budget or measured campaign data.
- Ohio's underperformance is a deliberate simulation input (disclosed in the report) with no real-world cause to investigate — a real deployment would need field-level data this project doesn't have.
