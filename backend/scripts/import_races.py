import re
from app.core.database import SessionLocal
from app.models.affiliations import Affiliation
from app.models.races import Race
from scripts.common import load_sheet, get_or_create

APOTHECARY_RE = re.compile(r"apothecary\s*\((yes|no)\)", re.IGNORECASE)
CHOICE_RE = re.compile(r"favoured of\s*\(\s*choose between (.+)\)", re.IGNORECASE)


def expand_rule_line(line):
    match = CHOICE_RE.match(line)
    if match is None:
        return [line]
    options = re.split(r",\s*(?:or\s+)?|\s+or\s+", match.group(1))
    return [f"Favoured of {o.strip()}" for o in options if o.strip()]


def parse_special_rules(raw):
    if not raw:
        return True, []
    text = str(raw)
    match = APOTHECARY_RE.search(text)
    allowed = True if match is None else match.group(1).lower() == "yes"
    rest = APOTHECARY_RE.sub("", text)
    lines = [line.strip() for line in rest.splitlines() if line.strip()]
    return allowed, lines


def to_int(value):
    return int(value) if value is not None else None


def main() -> None:
    ws = load_sheet("Races")
    processed = 0

    with SessionLocal() as db:
        for row in ws.iter_rows(min_row=2, values_only=True):
            
            # skip blank rows and "(S2)" entries
            if not row[0]:
                continue
            name = str(row[0]).strip()
            if "(S2)" in name:
                continue

            reroll = to_int(row[1])
            reroll_7s = to_int(row[2])
            leagues = [s.strip() for s in str(row[3] or "").split(",") if s.strip()] 
            tier = to_int(row[4])
            allowed, rule_lines = parse_special_rules(row[5])
            rule_names =[n for line in rule_lines for n in expand_rule_line(line)]
            all_names = set(leagues) | set(rule_names)
            affiliations = [get_or_create(db, Affiliation, n) for n in sorted(all_names)]
            
            race = get_or_create(
                db, 
                Race, 
                name, 
                tier=tier,
                reroll_cost=reroll,
                reroll_cost_7s=reroll_7s,
                apothecary_allowed=allowed,
                special_rule_text="\n".join(rule_names) or None,)
            
            race.affiliations = affiliations
            processed += 1

        db.commit()
    
    print(f"Done. {processed} races added.")

if __name__ == "__main__":
    main()