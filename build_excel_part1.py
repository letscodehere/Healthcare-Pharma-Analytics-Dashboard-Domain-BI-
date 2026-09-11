import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

DATA_DIR = "/home/claude/pharma_project/data"
OUT_DIR = "/home/claude/pharma_project/outputs"
XLSX_PATH = "/home/claude/pharma_project/excel/Pharma_Analytics_Dashboard.xlsx"

NAVY, TEAL, GOLD, RED = "1F3864", "2E8B8B", "D4A017", "B23A48"
LIGHT, YELLOW, WHITE = "EDF1F7", "FFF2CC", "FFFFFF"
WARNFILL = "FCE4D6"

HEADER_FONT = Font(name="Arial", bold=True, color=WHITE, size=11)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
TITLE_FONT = Font(name="Arial", bold=True, color=NAVY, size=18)
SUBTITLE_FONT = Font(name="Arial", italic=True, color="595959", size=10)
KPI_LABEL_FONT = Font(name="Arial", bold=True, color="595959", size=9)
KPI_VALUE_FONT = Font(name="Arial", bold=True, color=NAVY, size=16)
BODY_FONT = Font(name="Arial", size=10)
NOTE_FONT = Font(name="Arial", italic=True, size=9, color="808080")
WARN_FONT = Font(name="Arial", bold=True, size=11, color="9C4500")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
KPI_FILL = PatternFill("solid", fgColor=LIGHT)
COMPUTED_FILL = PatternFill("solid", fgColor=YELLOW)
WARN_FILL = PatternFill("solid", fgColor=WARNFILL)

data = pd.read_csv(f"{DATA_DIR}/pharma_prescribing_simulated.csv")
kpi = pd.read_csv(f"{OUT_DIR}/kpi_summary.csv", index_col=0).squeeze("columns")
ta_perf = pd.read_csv(f"{OUT_DIR}/therapy_area_performance.csv")
spec_perf = pd.read_csv(f"{OUT_DIR}/specialty_performance.csv")

N_ROWS = len(data)
LAST_ROW = N_ROWS + 1
DS = "'Data'"
COL = {name: get_column_letter(i + 1) for i, name in enumerate(data.columns)}

wb = Workbook()
wb.remove(wb.active)


def style_header_row(ws, row, ncols, start_col=1):
    for c in range(start_col, start_col + ncols):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def fast_write_large_df(ws, df, start_row=1):
    ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append(row)
    style_header_row(ws, start_row, len(df.columns))


def write_small_table(ws, df, start_row, start_col=1, table_name=None):
    for j, col in enumerate(df.columns):
        ws.cell(row=start_row, column=start_col + j, value=col)
    style_header_row(ws, start_row, len(df.columns), start_col)
    r0 = start_row + 1
    for i, row in enumerate(df.itertuples(index=False)):
        for j, val in enumerate(row):
            cell = ws.cell(row=r0 + i, column=start_col + j, value=val)
            cell.font = BODY_FONT
            cell.border = BORDER
    end_row = r0 + len(df) - 1
    if len(df) > 0:
        end_col_letter = get_column_letter(start_col + len(df.columns) - 1)
        start_col_letter = get_column_letter(start_col)
        ref = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
        tbl = Table(displayName=table_name, ref=ref)
        tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(tbl)
    return end_row


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def kpi_card(ws, row, col, label, value, is_computed=False, number_format=None):
    lbl_cell = ws.cell(row=row, column=col, value=label)
    lbl_cell.font = KPI_LABEL_FONT
    val_cell = ws.cell(row=row + 1, column=col, value=value)
    val_cell.font = KPI_VALUE_FONT
    if number_format:
        val_cell.number_format = number_format
    for rr in (row, row + 1):
        c = ws.cell(row=rr, column=col)
        c.fill = COMPUTED_FILL if is_computed else KPI_FILL
        c.border = BORDER
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 1)
    ws.merge_cells(start_row=row + 1, start_column=col, end_row=row + 1, end_column=col + 1)


# ====================================================================
# SHEET 1 — Read Me (prominent SIMULATED DATA notice)
# ====================================================================
ws = wb.create_sheet("Read Me")
ws["B2"] = "Healthcare / Pharma Analytics Dashboard"
ws["B2"].font = TITLE_FONT
ws["B3"] = "Excel Companion Workbook"
ws["B3"].font = SUBTITLE_FONT

ws["B5"] = "⚠ THIS DATASET IS SIMULATED — NOT REAL PATIENT, PHYSICIAN, OR PRESCRIBING DATA"
ws["B5"].font = WARN_FONT
ws["B5"].fill = WARN_FILL
for c in range(2, 9):
    ws.cell(row=5, column=c).fill = WARN_FILL
ws.merge_cells("B5:H5")
ws.row_dimensions[5].height = 20

rows_info = [
    ("Why simulated", "The only genuinely real public dataset with this exact shape (doctor-wise, "
                        "drug-wise, region-wise prescription volume) is CMS's Medicare Part D "
                        "Prescribers by Provider and Drug dataset — 25M+ rows / several GB, hosted "
                        "only on data.cms.gov, not bulk-downloadable in this environment. Rather than "
                        "use a tiny, unrepresentative real excerpt, this project builds a transparent, "
                        "clearly-labeled simulated dataset sized for a BI dashboard."),
    ("What makes it realistic", "The 16 drugs are real, currently-marketed drugs selected from the "
                                 "actual top Medicare Part D spending list (cited in README.md — CMS/"
                                 "KFF/AARP/Visual Capitalist reporting). Growth and decline trends "
                                 "follow real, publicly reported 2022-2024 directional patterns (e.g. "
                                 "Ozempic/Mounjaro's well-documented growth surge; Humira's well-"
                                 "documented 2023 biosimilar-driven decline). No real patient, "
                                 "physician, or NPI data is used anywhere — doctor names/IDs and every "
                                 "prescription count and dollar figure are entirely synthetic."),
    ("", ""),
    ("Dataset", "11,568 simulated monthly records: 83 synthetic doctors x 16 real drugs x 10 US "
                "states x 36 months (Jan 2022 - Dec 2024)."),
    ("", ""),
    ("Sheet guide", ""),
    ("Data", "The full simulated dataset. Every formula in this workbook reads from here."),
    ("Dashboard", "Top-line KPIs and therapy-area/specialty breakdowns. White cells are live "
                  "formulas; yellow cells are values computed in Python (growth-rate comparisons, "
                  "the underperforming-region flag, and the budget reallocation) because they need "
                  "multi-step ranking or period-over-period logic beyond a single formula."),
    ("Molecule and Therapy Uptake", "Molecule-level performance and growth/decline classification, "
                                     "with the uptake trend chart."),
    ("Regional Performance", "State- and region-level breakdown with the underperforming-region "
                              "flag and quantified opportunity gap."),
    ("Doctor Performance", "Top-prescriber ranking by specialty and state."),
    ("Budget Reallocation", "The quantified marketing-budget reallocation proposal and its "
                             "projected impact — clearly marked as an illustrative planning "
                             "assumption, not a guaranteed outcome."),
]
r = 7
for label, text in rows_info:
    ws.cell(row=r, column=2, value=label).font = Font(name="Arial", bold=True, size=10, color=NAVY)
    c = ws.cell(row=r, column=3, value=text)
    c.font = BODY_FONT
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 46 if text else 8
    r += 1

autosize(ws, {"A": 3, "B": 24, "C": 100})
ws.sheet_view.showGridLines = False

# ====================================================================
# SHEET 2 — Data
# ====================================================================
ws_data = wb.create_sheet("Data")
fast_write_large_df(ws_data, data)
ws_data.freeze_panes = "A2"
autosize(ws_data, {get_column_letter(i + 1): 15 for i in range(len(data.columns))})
print("Data sheet written.")

# ====================================================================
# SHEET 3 — Dashboard
# ====================================================================
ws = wb.create_sheet("Dashboard")
ws.sheet_view.showGridLines = False
ws["B2"] = "Healthcare / Pharma Analytics Dashboard"
ws["B2"].font = TITLE_FONT
ws["B3"] = "SIMULATED DATA | 83 Doctors | 16 Molecules | 10 States | Jan 2022 - Dec 2024"
ws["B3"].font = SUBTITLE_FONT

rx_rng = f"{DS}!${COL['prescriptions']}$2:${COL['prescriptions']}${LAST_ROW}"
cost_rng = f"{DS}!${COL['total_cost']}$2:${COL['total_cost']}${LAST_ROW}"
ta_rng = f"{DS}!${COL['therapy_area']}$2:${COL['therapy_area']}${LAST_ROW}"
spec_rng = f"{DS}!${COL['specialty']}$2:${COL['specialty']}${LAST_ROW}"

kpi_card(ws, 5, 2, "TOTAL PRESCRIPTIONS", f"=SUM({rx_rng})", number_format='#,##0')
kpi_card(ws, 5, 4, "TOTAL REVENUE (simulated)", f"=SUM({cost_rng})", number_format='$#,##0,,"M"')
kpi_card(ws, 5, 6, "DOCTORS", int(kpi["Doctors"]), is_computed=True, number_format='0')
kpi_card(ws, 5, 8, "MOLECULES TRACKED", int(kpi["Molecules Tracked"]), is_computed=True, number_format='0')

ws.cell(row=8, column=2, value=(
    "White cells = live formulas (recalculate if 'Data' changes). Yellow cells = values computed "
    "in Python — growth rates, underperforming-region flag, budget proposal (see Read Me)."
)).font = NOTE_FONT

r0 = 10
ws.cell(row=r0, column=2, value="Revenue by Therapy Area").font = Font(name="Arial", bold=True, size=12, color=NAVY)
hdr = ["Therapy Area", "Prescriptions", "Revenue"]
for j, h in enumerate(hdr):
    ws.cell(row=r0 + 1, column=2 + j, value=h)
style_header_row(ws, r0 + 1, len(hdr), 2)
therapy_areas = sorted(data["therapy_area"].unique().tolist())
for i, ta in enumerate(therapy_areas):
    rr = r0 + 2 + i
    ws.cell(row=rr, column=2, value=ta).font = BODY_FONT
    rx_cell = ws.cell(row=rr, column=3, value=f"=SUMIF({ta_rng},$B{rr},{rx_rng})")
    rx_cell.number_format = '#,##0'
    rev_cell = ws.cell(row=rr, column=4, value=f"=SUMIF({ta_rng},$B{rr},{cost_rng})")
    rev_cell.number_format = '$#,##0'
    for cc in range(2, 5):
        ws.cell(row=rr, column=cc).border = BORDER
row_after_ta = r0 + 2 + len(therapy_areas)

r1 = row_after_ta + 2
ws.cell(row=r1, column=2, value="Revenue by Specialty").font = Font(name="Arial", bold=True, size=12, color=NAVY)
for j, h in enumerate(hdr):
    ws.cell(row=r1 + 1, column=2 + j, value=h.replace("Therapy Area", "Specialty"))
style_header_row(ws, r1 + 1, len(hdr), 2)
specialties = sorted(data["specialty"].unique().tolist())
for i, sp in enumerate(specialties):
    rr = r1 + 2 + i
    ws.cell(row=rr, column=2, value=sp).font = BODY_FONT
    rx_cell = ws.cell(row=rr, column=3, value=f"=SUMIF({spec_rng},$B{rr},{rx_rng})")
    rx_cell.number_format = '#,##0'
    rev_cell = ws.cell(row=rr, column=4, value=f"=SUMIF({spec_rng},$B{rr},{cost_rng})")
    rev_cell.number_format = '$#,##0'
    for cc in range(2, 5):
        ws.cell(row=rr, column=cc).border = BORDER
row_after_spec = r1 + 2 + len(specialties)

autosize(ws, {"A": 2, "B": 30, "C": 16, "D": 18, "E": 4, "F": 20, "G": 20, "H": 20})

chart1 = BarChart()
chart1.type = "col"
chart1.title = "Revenue by Therapy Area"
data_ref = Reference(ws, min_col=4, min_row=r0 + 1, max_row=row_after_ta - 1)
cats_ref = Reference(ws, min_col=2, min_row=r0 + 2, max_row=row_after_ta - 1)
chart1.add_data(data_ref, titles_from_data=True)
chart1.set_categories(cats_ref)
chart1.height, chart1.width = 9, 16
ws.add_chart(chart1, "F10")

wb.save(XLSX_PATH)
print("Dashboard sheet written. Saved:", XLSX_PATH)
