import re
from collections import Counter, defaultdict

from app.core.database import SessionLocal
from app.models.affiliations import Affiliation
from app.models.mercenaries import Mercenary          # check your file and class name
from scripts.common import load_sheet, get_or_create

# cleans up data values store in sheet as different types {str, int, etc}
def num(value):
    if value is None:
        return 0
    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else 0

# removes trailing info
def base_name(raw):
    s = re.sub(r"\(\s*\d+\s*-\s*\d+\s*\)", "", str(raw))   # max allowed 
    s = re.sub(r"\(\s*\d+k\s*\)", "", s)                    # cost
    return re.sub(r"\s+", " ", s).strip()


def collect(ws):
    variants = defaultdict(Counter)
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0] or "(S2)" in str(row[0]) or not row[2]:
            continue
        variant = (
            num(row[1]),  # max_allowed
            num(row[3]), num(row[4]), num(row[5]), # MA, ST, AG
            num(row[6]), num(row[7]),  # PA, AV
            str(row[8]).strip() if row[8] else None, # skill_list
            num(row[9]), num(row[10]),  # cost, upkeep
            str(row[11]).strip() if row[11] else "",  # plays for
        )
        variants[base_name(row[2])][variant] += 1
    return variants

# completes all rows first before looking for most common value
def best_variant(counter): 
    return max(
        counter.items(),
        key=lambda item: (item[0][7] > 0 and item[0][9] != "", item[1]),
    )[0]
    
    
def main():
    ws = load_sheet("Mercenaries")
    variants = collect(ws)

    with SessionLocal() as db:
        for name, counter in sorted(variants.items()):
            (max_allowed, ma, st, ag, pa, av,
             skills, cost, upkeep, plays_for) = best_variant(counter)

            team_names = [t.strip().strip('"') for t in plays_for.split(",")]
            team_names = list(dict.fromkeys(t for t in team_names if t))
            affiliations = [get_or_create(db, Affiliation, t) for t in team_names]

            merc = get_or_create(
                db, 
                Mercenary, 
                name,
                max_allowed=max_allowed,
                movement=ma, 
                strength=st, 
                agility=ag, 
                passing=pa, 
                armor=av,
                skill_list=skills,
                cost=cost,
                upkeep=upkeep,
            )
            merc.affiliations = affiliations

        db.commit()

    print(f"Done. {len(variants)} mercenaries processed.")


if __name__ == "__main__":
    main()