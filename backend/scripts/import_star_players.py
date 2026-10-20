import re
from collections import Counter, defaultdict
from app.core.database import SessionLocal
from app.models.affiliations import Affiliation
from app.models.star_players import StarPlayer
from scripts.common import load_sheet, get_or_create

def clean_name(raw):
    name =re.sub(r"\s*\([^)]*\)", "", str(raw)) # removes additional info attached to name
    name = name.lstrip("* ") # removes leading marker
    name = re.split(r"\s+\*", name)[0] # Removes trailing notes
    return re.sub(r"\s+", " ", name).strip()


def is_inducement_only(raw):
    return "(inducement only)" in str(raw).lower()


def to_int(value):
    return int(value) if value is not None else 0


def collect(ws):
    variants = defaultdict(Counter)
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0] or "(S2)" in str(row[0]) or not row[2]:
            continue
        variant = (
            to_int(row[1]), # max allowed
            to_int(row[3]), to_int(row[4]), to_int(row[5]), # MA, ST, AG
            to_int(row[6]), to_int(row[7]), # PA, VA
            str(row[8]).strip() if row[8] else None, # SKills
            to_int(row[9]), to_int(row[10]), # cost & Upkeep
            str(row[11]).strip() if row[11] else "", # plays for
            str(row[12]).strip() if row[12] else None, # special rules
            is_inducement_only(row[2]),
        )
        variants[clean_name(row[2])][variant] += 1
    return variants

def main():
    ws = load_sheet("StarPlayers")
    variants = collect(ws)
    differing = []
    
    with SessionLocal() as db:
        for name, counter in sorted(variants.items()):
            if len(counter) > 1:
                differing.append((name, counter))
                
            (max_allowed, ma, st, ag, pa, av, skills, 
             cost, upkeep, plays_for, rule, inducement_only) = counter.most_common(1)[0][0]
            
            league_names = [s.strip() for s in plays_for.split(",") if s.strip()]
            affiliations = [get_or_create(db, Affiliation, n) for n in league_names]

            star_player = get_or_create(
                db,
                StarPlayer,
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
                special_rule=rule,
                inducement_only=inducement_only,
            )
            star_player.affiliations = affiliations
        db.commit()
    
    print(f"Done. {len(variants)} star players processed.")
    
if __name__ == "__main__":
    main()