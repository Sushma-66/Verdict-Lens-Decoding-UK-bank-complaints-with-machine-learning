# Learning guide: how this project works, file by file

Use this to practise. Go through the steps in order and make sure you can explain each one **in your own words**
before you talk about the project in an interview.

---

## Suggested practice plan (about 2 weeks, 1 hour a day)

| Day | Do this | You should be able to explain |
|---|---|---|
| 1 | Open `data/raw/fos_banking_decisions.csv` in Excel. Read 20 rows. | What a final decision is, what "upheld" means, what each column holds |
| 2 | Read `src/labels.py` top to bottom | Why firms are grouped; why the theme rules are in a specific order |
| 3 | Run notebook 01 cell by cell | Every cleaning step and why it's needed |
| 4–5 | Run notebook 02; change the "≥ 20 decisions" filter to 10 and to 40 | Why small samples give unreliable rates; what a confidence interval is |
| 6–7 | Run notebook 03 alongside ML-For-Beginners lessons 14–15 (clustering) | TF-IDF, K-Means, silhouette score, why scams split into several clusters |
| 8–10 | Run notebook 04 alongside ML-For-Beginners lessons 8 and 10–12 | Baseline, class imbalance, cross-validation, ROC-AUC, confusion matrix, coefficients |
| 11 | Run notebook 05 | Why counts over time are meaningless here; what the chi-square test shows |
| 12–13 | Build the Power BI dashboard (`powerbi/POWERBI_GUIDE.md`) | Measures vs columns; rates vs counts |
| 14 | Practise the interview answers below out loud | — |

**Challenge yourself:** after each notebook, change one thing (a rule, a parameter, a filter) and predict what will happen
**before** you re-run it. That's the fastest way to really understand it.

---

## File by file

### `data/raw/fos_banking_decisions.csv`
960 decisions exactly as collected. Never edit this file by hand; all changes happen in code, so they're repeatable.

### `src/labels.py`
Two jobs:
- **Firm grouping.** The ombudsman publishes the *legal entity* (e.g. "Bank of Scotland Plc"), but customers know the
  *brand* (Halifax). `FIRM_GROUPS` maps entities to groups; `firm_type()` puts each group into one of four types.
- **Theme rules.** `THEME_RULES` is an ordered list of regular expressions. The first match wins. Order matters:
  "fraud marker" must be caught as an account-closure complaint *before* the scam rule sees the word "fraud".

### `notebooks/01_data_cleaning.ipynb`
Checks for missing values and duplicates, fixes name variants, adds group/type/theme, creates the `upheld` flag and the
two-month `period`, and saves `decisions_clean.csv`.

### `notebooks/02_exploratory_analysis.ipynb`
Counts by theme, upheld rate by theme, upheld rate by banking group with confidence intervals, and a heatmap of the
complaint mix by firm type.

### `notebooks/03_complaint_themes_nlp.ipynb`
Unsupervised learning. Builds a custom stop-word list, turns text into TF-IDF vectors, picks the number of clusters with
the silhouette score, runs K-Means, and compares clusters with the rule-based themes.

### `notebooks/04_upheld_prediction.ipynb`
Supervised learning. Majority-class baseline vs logistic regression vs random forest, with 5-fold stratified
cross-validation on 75% of the data and a final test on the other 25%.

### `notebooks/05_trends_over_time.ipynb`
Upheld rate per window with confidence bands, a chi-square test comparing the two years, a within-theme check, and the
theme mix over time.

### `src/collect_fos_data.py`
Re-collects the data through the Apify API. You need your own Apify token (see the instructions at the top of the file).

---

## Key concepts in one line each

- **TF-IDF:** a word's weight = how often it appears in this complaint × how rare it is across all complaints.
- **K-Means:** puts each item in the group whose centre it's closest to, then moves the centres, and repeats.
- **Silhouette score:** how much closer each item is to its own cluster than to the next one (−1 to 1).
- **Adjusted Rand Index:** how much two groupings agree, corrected for chance (0 = random, 1 = identical).
- **Class imbalance:** only 27% of decisions are upheld, so a model that always says "not upheld" is 73% accurate and useless.
- **Balanced accuracy:** the average of the accuracy on each class, so the minority class counts equally.
- **ROC-AUC:** the probability the model ranks a random upheld case above a random not-upheld case.
- **Cross-validation:** train and test on 5 different splits and average, so one lucky split can't fool you.
- **Data leakage:** using information the model wouldn't have at prediction time. It gives fake high scores.
- **Confidence interval:** the range the true rate probably lies in; wide when the sample is small.
- **Chi-square test:** whether two categorical variables (here: year and outcome) are related by more than chance.

---

## Interview questions to practise

1. **"Walk me through this project."**
   Problem → data source → cleaning → themes → model → findings → limitations. Aim for 2 minutes.
2. **"Why did you use keyword rules instead of ML for the themes?"**
   Transparency for business users; I validated them with clustering and they agreed on the main themes.
3. **"Your model's ROC-AUC is only 0.63. Is that any good?"**
   It beats the baseline, and it's realistic given it only sees one sentence. I'd use it for triage, not decisions, and
   I know how to improve it (full decision text, more data).
4. **"Why not just use accuracy?"**
   Class imbalance: the baseline is 73% accurate by never predicting "upheld".
5. **"Can you say Santander is worse than Lloyds?"**
   Not confidently. The intervals are wide, and the difference could come from their different complaint mix.
6. **"The upheld rate fell. How do you know it isn't just a change in complaint mix?"**
   I compared the rate *within* each theme and it fell in most of them.
7. **"What would you do with more time?"**
   Full PDFs, embeddings, FOS volume data for forecasting, a published Power BI dashboard.
8. **"How did you get the data?"**
   FOS decisions are public, but there's no download. I used an Apify actor that reads the public search results, and
   the collection script is in the repo so it's reproducible.
