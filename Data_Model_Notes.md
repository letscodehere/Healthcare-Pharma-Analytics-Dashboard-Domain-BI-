# Power BI Data Model Notes

## Tables to import

| Table | Source file | Role |
|---|---|---|
| `Data` | `data/pharma_prescribing_simulated.csv` | Fact table — one row per doctor x molecule x month |
| `Doctors` | `data/doctors_reference.csv` | Dimension — one row per doctor (specialty, state, region) |
| `Molecules` | `data/molecules_reference.csv` | Dimension — one row per molecule (therapy area, real-world trend direction) |
| `States` | `data/states_reference.csv` | Dimension — one row per state (region, performance multiplier) |
| `BudgetReallocation` | `outputs/budget_reallocation.csv` | Standalone summary table for the Budget Reallocation page |
| `Date` | Created in Power BI (see below) | Standard date dimension for time intelligence |

`Data` already contains `doctor_name`, `specialty`, `state`, `region`,
`brand`, `therapy_area` denormalized directly on it, so the `Doctors` /
`Molecules` / `States` reference tables are optional — import them only if
you want a clean star schema with separate dimension tables and
relationships (recommended for a portfolio piece, since it demonstrates
proper data modeling rather than one flat table).

## Recommended star schema

If using the dimension tables:

```
Doctors[doctor_id]  1 -----> *  Data[doctor_id]
Molecules[brand]    1 -----> *  Data[brand]
States[state]       1 -----> *  Data[state]
Date[Date]          1 -----> *  Data[month]
```

Set every relationship to **Single** cross-filter direction, **Data** on the
many side. Do not create a relationship on `region` if you also relate
through `States[state]` → `Data[state]` — `region` would then be pulled in
via `States`, avoiding a redundant/ambiguous relationship.

## Building the Date table

Power BI's automatic date hierarchies are convenient but don't support
`SAMEPERIODLASTYEAR` cleanly against a monthly-only fact table. Build an
explicit one:

```dax
Date =
ADDCOLUMNS(
    CALENDAR(DATE(2022,1,1), DATE(2024,12,31)),
    "MonthYear", FORMAT([Date], "YYYY-MM"),
    "Year", YEAR([Date]),
    "MonthNum", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMM YYYY")
)
```

Then: Modeling → Mark as Date Table → select `Date[Date]`. Relate
`Date[Date]` to `Data[month]` (both are month-start dates, so this joins
cleanly one-to-one on the month level).

## Data types to verify after import

Power Query sometimes mis-detects types on a CSV this size. After importing
`Data`, check in Power Query Editor:
- `month` → **Date** (not Date/Time — the source values are already
  month-start dates like `2022-01-01`)
- `prescriptions`, `unique_patients` → **Whole Number**
- `total_cost` → **Fixed Decimal Number** or **Decimal Number**
- `doctor_id`, `state`, `region`, `molecule`, `brand`, `therapy_area`,
  `specialty` → **Text**

If `total_cost` imports as Text (occasionally happens with large CSVs and a
locale mismatch on the decimal separator), every DAX SUM measure will
silently return blank — this is the single most common thing to check if
your numbers don't match the Excel workbook.

## A reminder to carry onto every page of the report

Add a text box on the report's cover page: **"Simulated data — see
README.md."** This is a portfolio project; if you present it in an
interview, say so verbally too before anyone assumes it's a real client
deliverable.
