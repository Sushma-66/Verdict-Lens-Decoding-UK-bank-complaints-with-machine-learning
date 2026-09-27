"""
Helper rules used across the notebooks.

1. clean_business_name() + FIRM_GROUPS  -> tidy the business names and map each
   firm to its banking group (e.g. Halifax / Bank of Scotland -> Lloyds Banking Group).
2. assign_theme()                        -> a transparent, rule-based complaint theme
   based on keywords in the complaint text.

Keeping these rules in one file means every notebook uses exactly the same logic,
and you can explain each rule line by line in an interview.
"""

import re

# ---------------------------------------------------------------------------
# 1. Business name cleaning and grouping
# ---------------------------------------------------------------------------

# Some firms appear under more than one spelling in the raw data,
# e.g. "Monzo Bank Ltd" and "MONZO BANK LIMITED". We normalise them here.
NAME_FIXES = {
    "MONZO BANK LIMITED": "Monzo Bank Ltd",
    "NATIONAL WESTMINSTER BANK PUBLIC LIMITED COMPANY": "National Westminster Bank Plc",
    "MONEYBARN NO.1 LIMITED": "Moneybarn No. 1 Limited",
    "MARKS AND SPENCER FINANCIAL SERVICES PLC": "Marks & Spencer Financial Services plc",
    "BMW Financial Services(GB) Limited": "BMW Financial Services (GB) Limited",
    "American Express Services Europe Limited (AESEL)": "American Express Services Europe Limited",
    "Blue Motor Finance Ltd": "Blue Motor Finance Limited",
    "Advantage Finance Ltd": "Advantage Finance Limited",
    "Creation Consumer Finance Ltd": "Creation Consumer Finance Limited",
}

# Legal entity -> the banking group a customer would recognise.
# Only the main UK banking groups are listed; everything else is kept as its own name.
FIRM_GROUPS = {
    "Lloyds Bank PLC": "Lloyds Banking Group",
    "Bank of Scotland Plc": "Lloyds Banking Group",          # trades as Halifax
    "Black Horse Limited": "Lloyds Banking Group",           # Lloyds' car finance arm
    "Lex Autolease Ltd": "Lloyds Banking Group",
    "MBNA Limited": "Lloyds Banking Group",
    "National Westminster Bank Plc": "NatWest Group",
    "The Royal Bank of Scotland Plc": "NatWest Group",
    "Barclays Bank UK PLC": "Barclays",                      # includes Tesco Bank / Barclaycard
    "Clydesdale Financial Services Limited": "Barclays",     # trades as Barclays Partner Finance
    "HSBC UK Bank Plc": "HSBC UK",                           # includes first direct / M&S Bank
    "Santander UK Plc": "Santander UK",
    "Santander Consumer (UK) Plc": "Santander UK",
    "Nationwide Building Society": "Nationwide",
    "The Mortgage Works (UK) Plc": "Nationwide",
    "Clydesdale Bank Plc": "Virgin Money",
    "TSB Bank plc": "TSB",
    "Metro Bank PLC": "Metro Bank",
    "Monzo Bank Ltd": "Monzo",
    "Revolut Ltd": "Revolut",
    "Starling Bank Limited": "Starling",
    "J.P. Morgan Europe Limited": "Chase UK",
    "The Co-operative Bank Plc": "Co-operative Bank",
    "Kroo Bank Ltd": "Kroo",
}

# Which kind of firm is it? Used as a model feature and for filtering.
HIGH_STREET = {"Lloyds Banking Group", "NatWest Group", "Barclays", "HSBC UK",
               "Santander UK", "Nationwide", "Virgin Money", "TSB", "Metro Bank",
               "Co-operative Bank"}
DIGITAL = {"Monzo", "Revolut", "Starling", "Chase UK", "Kroo"}

CAR_FINANCE_WORDS = ("motor", "auto", "car ", "moneybarn", "motonovo", "startline",
                     "leaseplan", "arval", "oodle", "bmw", "mercedes", "volkswagen",
                     "toyota", "honda", "stellantis", "hyundai", "volvo", "tesla",
                     "rci financial", "leasys", "tandem motor", "n.i.i.b", "go car",
                     "carmoola", "billing finance", "firstrand", "mitsubishi hc")


def clean_business_name(name: str) -> str:
    name = str(name).strip()
    return NAME_FIXES.get(name, name)


def firm_group(clean_name: str) -> str:
    return FIRM_GROUPS.get(clean_name, clean_name)


def firm_type(group: str) -> str:
    g = group.lower()
    if group in HIGH_STREET:
        return "High-street bank"
    if group in DIGITAL:
        return "Digital bank / e-money"
    if any(w in g for w in CAR_FINANCE_WORDS):
        return "Car & consumer finance"
    return "Other lender / payment firm"


# ---------------------------------------------------------------------------
# 2. Rule-based complaint themes
# ---------------------------------------------------------------------------
# The ORDER matters: the first rule that matches wins. For example, "fraud marker"
# must be caught by the account-closure rule before the general scam rule sees "fraud".

THEME_RULES = [
    ("Account closure / fraud marker",
     r"cifas|fraud(?:-related)? marker|fraud prevention|fraud database|fraud alert|"
     r"closed (?:his|her|their|its|my) account|closed (?:the )?account|blocked|"
     r"restrict|suspend"),
    ("Timeshare / unfair credit (s140A)",
     r"140a|timeshare"),
    ("Mortgage",
     r"mortgage|buy[- ]to[- ]let|repossess"),
    ("Scam / APP fraud",
     r"scam|fraudster|authorised push payment|\bapp\b|defrauded|blackmail|"
     r"lost to fraud|as a result of fraud|investment fraud|fell victim|victim of"),
    ("Unauthorised transactions",
     r"(?:n[’']?t|not) (?:\w+ ){0,3}authoris|unauthorised|"
     r"(?:n[’']?t|not) recognise|didn[’']?t make|did not make|"
     r"disputed transactions|disputed payments|fraudulent transaction|"
     r"(?:didn[’']?t|did not) take out|without (?:his|her|their) knowledge"),
    ("Irresponsible lending",
     r"irresponsib|unaffordable|couldn[’']?t afford|could not afford|affordab|lent to|"
     r"checks .*(?:prior to|before) (?:approving|lending)"),
    ("Car finance - vehicle quality",
     r"(?:car|van|vehicle|motorbike|bike)\b.*(?:quality|satisfactory|fit for purpose|"
     r"faulty|reject|misrepresent|mis-represent)|"
     r"(?:quality|satisfactory).*(?:car|van|vehicle|motorbike)|"
     r"complain\w* about (?:a|the) (?:car|van|vehicle)|problems .*(?:car|van)"),
    ("Mis-selling, fees & charges",
     r"mis-?sold|mis-?sale|misled|mislead|mis-?informed|misinformed|incentive|"
     r"promotional|\bfees?\b|charges|charging|interest rate|packaged"),
    ("Refund claim (s75 / chargeback)",
     r"section 75|s\.?75|chargeback|charge back|money back|refund|"
     r"claim (?:he|she|they) made|handled (?:a|his|her) claim|\bdispute"),
    ("Credit file / debt / defaults",
     r"default|credit file|arrears|debt|statute barred|missed payment|"
     r"credit reference|write off|financial difficult"),
]

THEME_ORDER = [name for name, _ in THEME_RULES] + ["Service & administration"]


def assign_theme(text: str) -> str:
    t = str(text).lower()
    for name, pattern in THEME_RULES:
        if re.search(pattern, t):
            return name
    return "Service & administration"
