# Power BI dashboard guide

Build a one-page dashboard from `data/processed/decisions_clean.csv`. It takes about an hour and gives you a strong
visual for your portfolio and LinkedIn.

## 1. Load the data

1. Power BI Desktop → **Get data → Text/CSV** → `data/processed/decisions_clean.csv` → **Transform data**.
2. In Power Query, check the column types:
   - `decision_date`, `period_start` → **Date**
   - `upheld`, `text_length` → **Whole number**
   - everything else → **Text**
3. **Close & Apply**.

## 2. Measures (Modelling → New measure)

```DAX
Decisions = COUNTROWS(decisions_clean)

Upheld = SUM(decisions_clean[upheld])

Upheld Rate = DIVIDE([Upheld], [Decisions])

Scam Share =
DIVIDE(
    CALCULATE([Decisions], decisions_clean[theme] = "Scam / APP fraud"),
    [Decisions]
)

Upheld Rate vs Average =
[Upheld Rate] - CALCULATE([Upheld Rate], ALL(decisions_clean))
```

Format `Upheld Rate`, `Scam Share` and `Upheld Rate vs Average` as **Percentage, 0 decimal places**.

## 3. Page layout

| Position | Visual | Fields |
|---|---|---|
| Top row | 4 **Cards** | Decisions · Upheld Rate · Scam Share · count of distinct `firm_group` |
| Left, middle | **Clustered bar chart**: "What do customers complain about?" | Y: `theme` · X: `Decisions` · sort descending |
| Right, middle | **Clustered bar chart**: "Which complaints win?" | Y: `theme` · X: `Upheld Rate` · add a constant line at 27% |
| Bottom left | **Line chart**: "Upheld rate over time" | X: `period_start` · Y: `Upheld Rate` |
| Bottom right | **Matrix**: "Complaint mix by firm type" | Rows: `firm_type` · Columns: `theme` · Values: `Decisions`, shown as **percent of row total** · conditional formatting background colour |
| Side panel | **Slicers** | `firm_type`, `firm_group`, `sector`, `period` |

**Tip:** add a **Table** visual on a second page with `decision_date`, `firm_group`, `theme`, `outcome`, `complaint_text`
and `pdf_url` (set `pdf_url` as **Web URL** under Column tools → Data category) so viewers can click through to real decisions.

## 4. Things to say about it in an interview

- "I compared **rates, not counts**, because the data is a fixed sample per period."
- "I only show banks with 20+ decisions, and I'd add confidence intervals before anyone ranked banks from this."
- "The slicers let a complaints manager filter to their own firm type and see where their customers are winning."

## 5. Sharing

Publishing to the web requires a Power BI Pro licence or a work account. Free alternative: take screenshots of the
finished dashboard, save them in `reports/figures/` as `powerbi_dashboard.png`, and add them to the README.
`.pbix` files are excluded in `.gitignore` because they're large and can't be viewed on GitHub; remove that line if you
want to include yours.
