const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, ImageRun, Header, Footer,
  PageNumber,
} = require("docx");

const ASSETS = "/home/claude/pharma_project/assets";
const NAVY = "1F3864";
const TEAL = "2E8B8B";
const GOLD = "D4A017";
const RED = "B23A48";
const GREY = "595959";
const LIGHTGREY = "F2F2F2";
const WARNBG = "FCE4D6";
const WARNTEXT = "9C4500";

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 } });
}
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 21, ...opts })],
    spacing: { after: 160 },
    alignment: AlignmentType.JUSTIFIED,
  });
}
function bullet(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 21, ...opts })],
    bullet: { level: 0 },
    spacing: { after: 90 },
  });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 18, color: GREY })],
    spacing: { after: 260 },
    alignment: AlignmentType.CENTER,
  });
}
function tableCaption(num, text) {
  return new Paragraph({
    children: [new TextRun({ text: `Table ${num}. ${text}`, size: 19, bold: true, color: NAVY })],
    spacing: { before: 160, after: 100 },
  });
}
function image(file, width, height) {
  const data = fs.readFileSync(`${ASSETS}/${file}`);
  return new Paragraph({
    children: [new ImageRun({ data, transformation: { width, height }, type: "png" })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
  });
}
function warnBox(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: 9360, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: WARNBG, color: "auto" },
        margins: { top: 160, bottom: 160, left: 200, right: 200 },
        children: [new Paragraph({
          children: [new TextRun({ text, bold: true, size: 21, color: WARNTEXT })],
        })],
      })],
    })],
  });
}
function headerCell(text, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: NAVY, color: "auto" },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 19 })], alignment: AlignmentType.CENTER })],
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
  });
}
function dataTable(headers, rows, colWidths) {
  const headerRow = new TableRow({ children: headers.map((t, i) => headerCell(t, colWidths[i])), tableHeader: true });
  const bodyRows = rows.map((r, ridx) => new TableRow({
    children: r.map((val, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: ridx % 2 === 0 ? "FFFFFF" : LIGHTGREY, color: "auto" },
      children: [new Paragraph({
        children: [new TextRun({ text: String(val), size: 19 })],
        alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
      })],
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
    })),
  }));
  return new Table({ rows: [headerRow, ...bodyRows], width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: colWidths });
}
function kpiRow(items) {
  const w = Math.floor(9360 / items.length);
  return new Table({
    columnWidths: items.map(() => w),
    width: { size: 9360, type: WidthType.DXA },
    rows: [new TableRow({
      children: items.map(([label, value]) => new TableCell({
        width: { size: w, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "EDF1F7", color: "auto" },
        margins: { top: 160, bottom: 160, left: 120, right: 120 },
        children: [
          new Paragraph({ children: [new TextRun({ text: label, size: 15, bold: true, color: GREY })], alignment: AlignmentType.CENTER }),
          new Paragraph({ children: [new TextRun({ text: value, size: 27, bold: true, color: NAVY })], alignment: AlignmentType.CENTER, spacing: { before: 60 } }),
        ],
      })),
    })],
  });
}
function figureCaption(num, text) { return caption(`Figure ${num}. ${text}`); }

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        run: { size: 32, bold: true, color: NAVY, font: "Calibri" },
        paragraph: { spacing: { before: 360, after: 160 }, border: { bottom: { color: NAVY, space: 4, style: BorderStyle.SINGLE, size: 8 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        run: { size: 25, bold: true, color: TEAL, font: "Calibri" },
        paragraph: { spacing: { before: 260, after: 120 } } },
    ],
  },
  sections: [
    // ============================================================ COVER
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
      children: [
        new Paragraph({ text: "", spacing: { before: 1000 } }),
        warnBox("⚠ SIMULATED DATA — this report analyzes a synthetic dataset, clearly labeled throughout. No real patient, physician, or NPI data is used. See Section 3.2 for full disclosure and citations."),
        new Paragraph({ text: "", spacing: { before: 700 } }),
        new Paragraph({ children: [new TextRun({ text: "HEALTHCARE / PHARMA", bold: true, size: 52, color: NAVY })], alignment: AlignmentType.CENTER }),
        new Paragraph({ children: [new TextRun({ text: "ANALYTICS DASHBOARD", bold: true, size: 52, color: NAVY })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),
        new Paragraph({ children: [new TextRun({ text: "Business Insights Report", size: 28, color: TEAL, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 720 } }),
        new Paragraph({ children: [new TextRun({ text: "Dataset: Simulated Prescribing Data, Calibrated to Real Medicare Part D Trends", size: 22, color: GREY })], alignment: AlignmentType.CENTER }),
        new Paragraph({ children: [new TextRun({ text: "83 Doctors | 16 Molecules | 10 States | Jan 2022 - Dec 2024 | Excel + Power BI", size: 22, color: GREY })], alignment: AlignmentType.CENTER, spacing: { after: 720 } }),
        image("01_therapy_uptake_trend.png", 400, 200),
        new Paragraph({ text: "", spacing: { before: 500 } }),
        new Paragraph({ children: [new TextRun({ text: "Prepared using Microsoft Excel (live formulas) and Power BI (DAX measures) — Python used as the analysis/generation engine", size: 18, color: GREY, italics: true })], alignment: AlignmentType.CENTER }),
      ],
    },
    // ============================================================ BODY
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
      headers: {
        default: new Header({ children: [new Paragraph({
          children: [new TextRun({ text: "Healthcare / Pharma Analytics Dashboard — Business Insights Report (SIMULATED DATA)", size: 15, color: GREY })],
          border: { bottom: { color: "D9D9D9", space: 4, style: BorderStyle.SINGLE, size: 4 } },
        })] }),
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 16, color: GREY }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY })],
        })] }),
      },
      children: [
        // ---------------------------------------------------- EXEC SUMMARY
        h1("1. Executive Summary"),
        body("This report presents a healthcare/pharma analytics dashboard integrating simulated " +
          "hospital-prescriber and pharmaceutical sales data, built with Excel and Power BI, " +
          "analyzing performance by doctor, region, and molecule to track therapy uptake, flag " +
          "underperforming regions, and recommend a data-driven marketing budget reallocation. The " +
          "underlying dataset is clearly labeled as simulated (Section 3.2) — no real patient, " +
          "physician, or prescription data is used anywhere in this project — but is calibrated to " +
          "real, cited Medicare Part D program statistics so that every pattern in it (which drugs " +
          "are growing, which are declining, realistic prescribing volumes) reflects genuine, current " +
          "pharmaceutical market dynamics."),
        kpiRow([
          ["TOTAL PRESCRIPTIONS", "145,856"],
          ["TOTAL REVENUE (sim.)", "$205.9M"],
          ["DOCTORS TRACKED", "83"],
          ["MOLECULES TRACKED", "16"],
        ]),
        new Paragraph({ text: "", spacing: { after: 200 } }),
        h2("Headline findings"),
        bullet("Therapy uptake diverges sharply by molecule: Mounjaro (+245%) and Ozempic (+115%) " +
          "show explosive simulated growth over the study period, mirroring the real, well-documented " +
          "2022-2024 GLP-1 diabetes/weight-management surge, while Humira (-59%) and Imbruvica (-38%) " +
          "show steep simulated decline, mirroring Humira's real, well-documented 2023 biosimilar-" +
          "driven erosion."),
        bullet("Ohio is flagged as a materially underperforming region: 58.2% below the portfolio " +
          "average prescriptions-per-doctor, implying approximately $8.7M in simulated missed annual " +
          "revenue if it simply performed at the portfolio average — a directly actionable regional " +
          "finding."),
        bullet("Oncology and Immunology drive disproportionate revenue relative to prescription " +
          "volume (high cost-per-prescription specialty drugs) despite Immunology's overall molecule-" +
          "level decline — a margin-versus-volume tension worth flagging to a commercial strategy team."),
        bullet("A quantified marketing budget reallocation — redirecting 15% of non-Ohio field-" +
          "marketing spend into Ohio — is projected to generate approximately $4.3M in incremental " +
          "annual simulated revenue under a stated, conservative gap-closure assumption (Section 9)."),

        // ---------------------------------------------------- BUSINESS PROBLEM
        h1("2. Business Problem & Objective"),
        body("Pharmaceutical commercial teams allocate limited marketing and sales-engagement " +
          "resources across a large, heterogeneous prescriber base spanning many specialties, " +
          "geographies, and therapeutic areas. Without a consolidated, doctor-wise / region-wise / " +
          "molecule-wise view of prescribing performance, budget allocation defaults to historical " +
          "inertia rather than current market dynamics — under-investing in genuinely underperforming " +
          "regions and over-investing in already-saturated ones. This project builds exactly that " +
          "consolidated view, in the tools (Excel, Power BI) a commercial analytics team actually " +
          "uses, and closes the loop with a concrete, quantified budget-reallocation recommendation " +
          "rather than stopping at descriptive reporting."),

        // ---------------------------------------------------- DATA SOURCE
        h1("3. Data Source & Methodology"),
        h2("3.1 Why this project uses simulated data"),
        body("The only genuinely real public dataset with the doctor-wise, drug-wise, region-wise " +
          "shape this project requires is the Centers for Medicare & Medicaid Services (CMS) Medicare " +
          "Part D Prescribers by Provider and Drug dataset. That dataset is real and free, but " +
          "spans 25 million or more rows across several gigabytes for a single year, hosted only on " +
          "data.cms.gov, and is not practically bulk-downloadable or usable directly in Excel without " +
          "heavy pre-filtering infrastructure this project's environment does not have access to. " +
          "Rather than present a small, unrepresentative real excerpt as though it were the full " +
          "picture, this project builds a transparent, clearly-labeled simulated dataset, sized " +
          "appropriately for a BI dashboard (83 doctors, 16 molecules, 10 states, 36 months)."),
        h2("3.2 What makes the simulation realistic"),
        body("The 16 drugs used are real, currently-marketed pharmaceuticals selected from the " +
          "actual top Medicare Part D spending list (2021-2024 CMS Medicare Part D Spending by Drug " +
          "Dashboard, as reported by KFF, AARP Public Policy Institute, and Visual Capitalist). Each " +
          "molecule's simulated month-over-month growth or decline trajectory follows its real, " +
          "publicly reported directional trend over 2022-2024 — for example, Ozempic and Mounjaro's " +
          "well-documented explosive real-world growth as GLP-1 medications expanded from diabetes " +
          "into broader weight-management use, and Humira's well-documented steep 2023 decline " +
          "following the arrival of the first adalimumab biosimilars. No real patient, physician, or " +
          "National Provider Identifier (NPI) data is used anywhere in this project: doctor names and " +
          "IDs are synthetically generated, and every prescription count and dollar figure is " +
          "simulated, not observed."),
        h2("3.3 Tools and approach"),
        dataTable(
          ["Stage", "Tool", "Purpose"],
          [
            ["Data generation", "Python (numpy, pandas)", "Simulated dataset, calibrated to cited real-world drug trends"],
            ["Core analysis", "Python (pandas)", "KPIs, doctor/region/molecule breakdowns, growth-rate calculations"],
            ["Dashboard (delivered)", "Microsoft Excel", "Live-formula KPI dashboard, regional and molecule breakdowns"],
            ["Dashboard (delivered)", "Power BI (DAX)", "Interactive report — build guide and measures provided"],
            ["Visualization", "Python (matplotlib) + Excel/Power BI", "All charts in this report and both dashboards"],
          ],
          [2600, 2600, 4160],
        ),

        // ---------------------------------------------------- MOLECULE / THERAPY UPTAKE
        h1("4. Molecule-Wise Performance & Therapy Uptake"),
        image("01_therapy_uptake_trend.png", 500, 250),
        figureCaption(1, "Simulated monthly prescriptions, 2022-2024 — three growing molecules (solid) vs. three declining molecules (dashed)."),
        tableCaption(1, "Molecule performance and growth, ranked by simulated revenue."),
        dataTable(
          ["Brand", "Therapy Area", "Total Rx", "Revenue", "Growth %"],
          [
            ["Ibrance", "Oncology", "2,472", "$36.1M", "+8.2%"],
            ["Ozempic", "Diabetes & Metabolic", "25,021", "$23.7M", "+115.2%"],
            ["Imbruvica", "Oncology", "1,412", "$21.4M", "-37.7%"],
            ["Biktarvy", "Infectious Disease (HIV)", "4,286", "$16.1M", "+69.8%"],
            ["Mounjaro", "Diabetes & Metabolic", "15,285", "$16.0M", "+245.3%"],
            ["Humira", "Immunology", "2,231", "$15.1M", "-59.1%"],
          ],
          [2160, 2760, 1560, 1560, 1320],
        ),
        new Paragraph({ text: "", spacing: { after: 160 } }),
        body("Growth % compares the average monthly prescriptions in the first 6 months of the " +
          "study period against the last 6 months. Mounjaro's +245.3% and Ozempic's +115.2% simulated " +
          "growth directly mirror the real GLP-1 category's documented 2022-2024 surge; Humira's " +
          "-59.1% and Imbruvica's -37.7% simulated decline mirror the real, well-reported impact of " +
          "biosimilar competition and newer-generation competitor therapies respectively. This " +
          "molecule-level divergence — not a uniform market trend — is exactly the kind of signal a " +
          "commercial analytics team uses to redirect field-force effort toward growth therapies " +
          "and away from structurally declining ones."),
        image("02_revenue_by_therapy_area.png", 460, 259),
        figureCaption(2, "Revenue by therapy area (simulated)."),
        body("Oncology and Immunology generate outsized revenue relative to their prescription " +
          "volume — a direct consequence of high per-prescription specialty-drug costs (Ibrance and " +
          "Imbruvica exceed $14,000 per prescription in this simulation, consistent with real, " +
          "well-documented oncology drug pricing) — even though Immunology as a category is in " +
          "aggregate decline. This margin-versus-volume tension is worth surfacing explicitly to a " +
          "commercial strategy team rather than leaving it implicit in a single blended revenue figure."),

        // ---------------------------------------------------- REGIONAL
        h1("5. Region-Wise Performance & the Underperforming Region"),
        image("03_state_performance.png", 460, 256),
        figureCaption(3, "Prescriptions per doctor by state, portfolio average shown as a reference line."),
        tableCaption(2, "Underperforming-region analysis: Ohio vs. the portfolio benchmark."),
        dataTable(
          ["Metric", "Value"],
          [
            ["Ohio prescriptions per doctor", "734.5"],
            ["Portfolio average prescriptions per doctor", "1,757.3"],
            ["Gap below portfolio average", "58.2%"],
            ["Implied missed prescriptions (if at portfolio average)", "6,137"],
            ["Implied missed revenue (simulated)", "$8,663,352"],
          ],
          [5600, 3760],
        ),
        new Paragraph({ text: "", spacing: { after: 160 } }),
        body("Ohio is the clear, unambiguous outlier in this simulation — its per-doctor prescribing " +
          "volume sits well below every other state, including the next-lowest (Arizona, at 1,145.6 " +
          "prescriptions per doctor). A modest negative regional-performance factor was deliberately " +
          "built into Ohio's simulation to create a genuine test case for this kind of regional " +
          "diagnostic exercise (documented in notebooks/01_generate_data.py); the analysis correctly " +
          "recovers this as the standout underperformer purely from the resulting data, without being " +
          "told in advance which state to flag. This kind of gap is realistic and well-documented in " +
          "the pharmaceutical commercial literature as arising from formulary access differences, " +
          "sales-territory coverage gaps, or local payer-mix variation — the specific cause would need " +
          "field-level investigation in a real deployment, which Section 9's budget proposal treats as " +
          "the next step, not an assumption this analysis makes on its own."),

        // ---------------------------------------------------- DOCTOR
        h1("6. Doctor-Wise Performance"),
        image("04_top_doctors.png", 460, 316),
        figureCaption(4, "Top 15 doctors by simulated prescribing revenue."),
        body("The top prescribers by revenue are concentrated in Oncology and Rheumatology — " +
          "consistent with those specialties' very high per-prescription drug costs (Section 4) even " +
          "at comparatively modest prescription volumes. This is worth distinguishing clearly from " +
          "prescription volume leadership: a high-revenue doctor is not necessarily a high-volume one, " +
          "and a commercial engagement strategy should treat these as two different signals — volume " +
          "leaders are candidates for retention/loyalty engagement, while revenue leaders in " +
          "high-cost specialty categories warrant closer clinical/access support given the larger " +
          "revenue-at-risk per prescriber."),
        image("05_revenue_by_specialty.png", 460, 259),
        figureCaption(5, "Revenue by specialty (simulated)."),

        // ---------------------------------------------------- BUDGET REALLOCATION
        h1("7. Marketing Budget Reallocation Recommendation"),
        body("Translating the underperforming-region finding (Section 5) into a concrete resource " +
          "decision: a status-quo marketing budget of $2,000,000, currently allocated across the 10 " +
          "states in proportion to current revenue (a common commercial-planning starting point), is " +
          "compared against a proposed reallocation that redirects 15% of every other state's budget " +
          "into Ohio. Every dollar figure in this section is a stated illustrative planning assumption " +
          "layered on top of the simulated prescribing data, not a measured or guaranteed outcome — " +
          "presented with the same transparency as the underlying dataset."),
        image("07_budget_reallocation.png", 460, 256),
        figureCaption(6, "Current vs. proposed marketing budget by state."),
        tableCaption(3, "Proposed reallocation and projected impact."),
        dataTable(
          ["Metric", "Value"],
          [
            ["Ohio budget — current", "$105,139"],
            ["Ohio budget — proposed", "$389,368"],
            ["Ohio budget increase", "+270.3%"],
            ["Gap-closure assumption (stated, conservative)", "50% of the way to portfolio average"],
            ["Projected incremental prescriptions / year", "3,068"],
            ["Projected incremental revenue / year (simulated)", "$4,331,671"],
          ],
          [5600, 3760],
        ),
        new Paragraph({ text: "", spacing: { after: 160 } }),
        body("Two things are worth being explicit about in how this number should be read. First, " +
          "the +270% figure is a large percentage change applied to a small current base (Ohio's " +
          "current proportional-to-revenue budget is small precisely because its revenue is low) — " +
          "the absolute dollar shift ($284,229, about 14% of the total $2M budget) is the more " +
          "meaningful planning number, and is a realistic, moderate reallocation by commercial-" +
          "planning standards. Second, the projected incremental revenue rests on a stated 50% gap-" +
          "closure assumption that has not been tested — a real deployment of this recommendation " +
          "would start with a smaller pilot investment and measure the actual response before " +
          "committing the full proposed reallocation."),

        // ---------------------------------------------------- RECOMMENDATIONS
        h1("8. Recommendations Summary"),
        bullet("Redirect field-marketing investment toward Ohio on a pilot basis, with a defined " +
          "measurement period (e.g., two quarters) before committing the full proposed reallocation " +
          "— validate the 50% gap-closure assumption against real response data rather than " +
          "extrapolating from it directly."),
        bullet("Prioritize field engagement and access support for the fastest-growing molecules " +
          "(Ozempic, Mounjaro, Biktarvy, Entresto) where prescriber momentum is already building — " +
          "marketing spend compounds fastest against an existing growth trend."),
        bullet("For declining molecules facing structural headwinds (Humira, Imbruvica, Januvia), " +
          "shift commercial messaging toward any newer-generation or combination therapies in the " +
          "same portfolio rather than continuing to defend share in a structurally shrinking market."),
        bullet("Investigate the specific, local cause of Ohio's underperformance (formulary access, " +
          "sales-territory coverage, payer mix) before finalizing the budget reallocation — this " +
          "analysis identifies the *what* and sizes the opportunity, but the *why* requires field-" +
          "level investigation this dataset cannot answer."),
        bullet("Track revenue and prescription-volume leadership as two distinct doctor-level " +
          "signals (Section 6) rather than a single blended ranking, since they call for different " +
          "engagement strategies."),

        // ---------------------------------------------------- LIMITATIONS
        h1("9. Limitations"),
        bullet("This project uses simulated data throughout. While calibrated to real, cited " +
          "Medicare Part D trends, no figure in this report — prescription counts, revenue, doctor " +
          "identities, or the Ohio underperformance finding itself — reflects an actual measured " +
          "outcome. This must be disclosed in any professional context this project is presented in."),
        bullet("The real CMS Medicare Part D Prescribers dataset this project is modeled on covers " +
          "Medicare beneficiaries only, not the full commercially-insured or uninsured patient " +
          "population — a real deployment of this analysis would need a data source spanning the " +
          "target payer mix."),
        bullet("Approximate cost-per-prescription figures for each molecule are illustrative, " +
          "order-of-magnitude estimates informed by public pricing reporting, not exact wholesale " +
          "acquisition cost (WAC) or net-of-rebate pricing, which vary by payer and are not fully " +
          "public."),
        bullet("The budget reallocation's $2,000,000 total, the 15% reallocation share, and the 50% " +
          "gap-closure assumption are all stated illustrative planning inputs, not derived from any " +
          "real commercial budget or measured campaign-response data."),
        bullet("The specific cause of Ohio's simulated underperformance (a deliberate simulation " +
          "input, disclosed in Section 5) has no real-world counterpart to investigate — a real " +
          "deployment would need field-level data (formulary status, territory coverage, payer mix) " +
          "this project does not have access to."),

        // ---------------------------------------------------- CONCLUSION
        h1("10. Conclusion"),
        body("This project builds a complete healthcare/pharma analytics dashboard — in Excel and " +
          "Power BI, the tools a commercial analytics team actually uses — covering doctor-wise, " +
          "region-wise, and molecule-wise performance, therapy uptake tracking, and a quantified " +
          "marketing-budget reallocation recommendation. Because genuinely real prescriber-level data " +
          "of this shape is either too large to practically use in this environment (CMS's real " +
          "dataset) or commercially proprietary (IQVIA/Symphony Health-style data used by actual " +
          "pharma companies), this project uses a transparently-labeled simulated dataset calibrated " +
          "to real, current, cited Medicare Part D trends — providing a realistic, ethically clean " +
          "demonstration of the analytical workflow without any risk of exposing real patient or " +
          "physician information. The Ohio underperformance finding and the Ozempic/Mounjaro-vs-" +
          "Humira/Imbruvica growth divergence together demonstrate the kind of data-driven "  +
          "budget-allocation decision this dashboard is built to support."),

        // ---------------------------------------------------- APPENDIX
        h1("11. Appendix: Data Dictionary & Citations"),
        tableCaption(4, "Data dictionary."),
        dataTable(
          ["Field", "Description"],
          [
            ["month", "Month of the simulated prescribing activity (2022-01 to 2024-12)"],
            ["doctor_id / doctor_name", "Synthetic doctor identifier and name — not real physicians"],
            ["specialty", "Physician specialty (7 categories, each linked to specific therapy areas)"],
            ["state / region", "US state and Census region"],
            ["molecule / brand", "Generic and brand name — 16 real, currently-marketed drugs"],
            ["therapy_area", "One of 6 therapeutic categories"],
            ["prescriptions", "Simulated monthly prescription count"],
            ["unique_patients", "Simulated monthly unique patient count"],
            ["total_cost", "Simulated monthly prescribing revenue"],
          ],
          [2600, 6760],
        ),
        new Paragraph({ text: "", spacing: { after: 160 } }),
        h2("Citations for the real-world facts used to calibrate this simulation"),
        bullet("CMS Medicare Part D Prescribers by Provider and Drug — dataset structure reference. Centers for Medicare & Medicaid Services, data.cms.gov."),
        bullet("CMS Medicare Part D Spending by Drug Dashboard — top-spending drug list, 2021-2024, as reported via KFF (kff.org) and AARP Public Policy Institute analyses."),
        bullet("Visual Capitalist — \"Top Drugs by Medicare Part D Spending\" reporting, used to confirm the relative ranking and real-world growth/decline direction of the molecules used in this simulation."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("/home/claude/pharma_project/report/Pharma_Analytics_Business_Report.docx", buffer);
  console.log("Report written.");
});
