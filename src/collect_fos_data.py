"""
Collect Financial Ombudsman Service (FOS) final decisions for the banking sector
using the Apify actor "spookyweb/uk-fos-decisions".

This is how data/raw/fos_banking_decisions.csv was built:
  - sector: banking, credit and mortgages
  - 12 two-month windows from Sep 2024 to Aug 2026
  - the 80 most recent decisions in each window (960 in total)

Usage
-----
1. Create a free Apify account and copy your API token (Apify Console > Settings > Integrations).
2. In a terminal:
       pip install apify-client pandas
       export APIFY_TOKEN="your_token_here"          # Windows: set APIFY_TOKEN=your_token_here
       python src/collect_fos_data.py
3. The script writes data/raw/fos_banking_decisions_new.csv (it won't overwrite the original).

Cost: the actor charges about $0.001 per decision on Apify's free tier, so 960 decisions ≈ $1.
Note: free Apify accounts can only run 5 actors at the same time, so windows run one after another.
"""

import os
import re
from pathlib import Path

import pandas as pd
from apify_client import ApifyClient

ACTOR = "spookyweb/uk-fos-decisions"
PER_WINDOW = 80
WINDOWS = [  # (date_from, date_to) in DD/MM/YYYY, as the actor expects
    ("01/09/2024", "31/10/2024"), ("01/11/2024", "31/12/2024"),
    ("01/01/2025", "28/02/2025"), ("01/03/2025", "30/04/2025"),
    ("01/05/2025", "30/06/2025"), ("01/07/2025", "31/08/2025"),
    ("01/09/2025", "31/10/2025"), ("01/11/2025", "31/12/2025"),
    ("01/01/2026", "28/02/2026"), ("01/03/2026", "30/04/2026"),
    ("01/05/2026", "30/06/2026"), ("01/07/2026", "31/08/2026"),
]
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "fos_banking_decisions_new.csv"


def opening_sentence(summary: str) -> str:
    """Keep the part of the summary that describes the complaint: after 'The complaint' and before 'What happened'."""
    text = re.sub(r"^\s*\d*\s*DRN-\d+\s*", "", str(summary))           # drop a leading page number / reference
    text = re.sub(r"^\s*(the complaint( and what happened)?|complaint)\s*", "", text, flags=re.I)
    text = re.split(r"\s(?:What happened|Background|What’s happened\?)\s", text)[0]
    return text.rstrip(". ").strip() + "."


def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("Set the APIFY_TOKEN environment variable first (see the docstring at the top).")

    client = ApifyClient(token)
    frames = []
    for date_from, date_to in WINDOWS:
        print(f"Collecting {date_from} to {date_to} ...")
        run = client.actor(ACTOR).call(run_input={
            "sector": "banking-credit-mortgages",
            "dateFrom": date_from,
            "dateTo": date_to,
            "maxResults": PER_WINDOW,
        })
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        frames.append(pd.DataFrame(items).head(PER_WINDOW))

    raw = pd.concat(frames, ignore_index=True).drop_duplicates("reference")
    df = pd.DataFrame({
        "reference": raw["reference"],
        "decision_date": raw["date"],
        "outcome": raw["outcome"],
        "business": raw["business"],
        "sector": raw["sector"],
        "complaint_text": raw["summary"].map(opening_sentence),
        "pdf_url": raw["pdfUrl"],
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} decisions to {OUT}")


if __name__ == "__main__":
    main()
