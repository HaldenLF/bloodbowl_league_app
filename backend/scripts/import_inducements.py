import re
from collections import Counter

from app.core.database import SessionLocal
from app.models.affiliations import Affiliation
from app.models.inducements import Inducement
from scripts.common import load_sheet, get_or_create

CODES = {
    "B&C": "Bribery & Corruption", "BB": "Badlands Brawl", "CC": "Chaos Clash",
    "EKL": "Elven Kingdoms League", "HTC": "Halfling Thimble Cup",
    "LS": "Lustrian Superleague", "LL": "Lustrian Superleague",
    "OWC": "Old World Classic", "SS": "Sylvanian Spotlight",
    "UC": "Underworld Challenge", "WES": "Worlds Edge Superleague",
    "WL": "Woodland League", "FO...": "Favoured of...",
    "FOT": "Favoured of Tzeentch", "FOH": "Favoured of Hashut",
    "FO...Nurgle": "Favoured of Nurgle", "Halflings": "Halfling Teams",
    "HT": "Halfling Teams", "LCL": "Low Cost Linemen", "LCC": "Low Cost Linemen",
    "MOU": "Masters of Undeath",
}
SKIP_PREFIXES = ("mercenary player", "star player")


def base_name(raw):
    s = re.sub(r"\(\s*\d+\s*-\s*\d+\s*\)", "", str(raw))      # remove number allowed notation
    s = re.sub(r"\(\s*\d+k\s*\)", "", s)                       # remove cost notation
    s = re.sub(r"\*\s*([^*]+?)\s*\*", lambda m: "*" + m.group(1).strip() + "*", s)  
    return re.sub(r"\s+", " ", s).strip()


def tags(raw):
    return [t.strip() for t in re.findall(r"\*([^*]+)\*", str(raw)) if t.strip()]


def header(raw):
    s = re.sub(r"\(\s*\d+\s*-\s*\d+\s*\)", "", str(raw))   # remove number allowed notation
    return s.replace("-", "").strip()                       # followed by dashes

def collect(ws):
    rows = []
    category = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        label = str(row[0]).strip()
        if label.startswith("-----"): # section head
            category = header(label)
            if category == "Code": # inducements
                break
            continue
        if label == "None" or label.lower().startswith(SKIP_PREFIXES):
            continue
        rows.append((
            category,
            label,
            int(str(row[1]).split("-")[1]), # max allowed
            int(row[2]), # cost column
            str(row[3]).strip() if row[3] else None,
        ))
    return rows


def main ():
    ws = load_sheet("Inducements")
    rows = collect(ws)
    name_count = Counter(base_name(label) for _, label, *_ in rows)
    
    with SessionLocal() as db:
        for category, label, max_allowed, cost, rule in rows:
            name = base_name(label)
            if name_count[name] > 1: # side bets
                name = f"{name} ({cost // 1000}k)"
                
            tag_names = list(dict.fromkeys(CODES.get(t, t) for t in tags(label)))
            affiliations = [get_or_create(db, Affiliation, n) for n in tag_names]
            
            inducement = get_or_create(
                db,
                Inducement,
                name,
                category=category,
                max_allowed=max_allowed,
                cost=cost,
                description=rule,
            )
            inducement.affiliations = affiliations
        
        db.commit()
        
    print(f"Done. {len(rows)} inducements processed")

if __name__ == "__main__":
    main()