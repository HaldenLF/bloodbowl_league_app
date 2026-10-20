import re
from app.core.database import SessionLocal
from app.models.affiliations import Affiliation
from app.models.races import Race
from scripts.common import load_sheet, get_or_create

APOTHECARY_RE = re.compile(r"apothecary\s*\((yes|no)\)", re.IGNORECASE)
CHOICE_RE = re.compile(r"favoured of\s*\(\s*choose between (.+)\)", re.IGNORECASE)


def main() -> None:
    ws = load_sheet("Races")
    added = 0   # races created, for the final print

    with SessionLocal() as db:
        for row in ws.iter_rows(min_row=2, values_only=True):

            # 1. Skip junk rows
            #    - name blank       -> continue
            #    - "(S2)" in name   -> continue

            # 2. Pull the plain values out of the row
            #    name        = row[0], stripped
            #    reroll      = row[1]  \  numbers, but may be None,
            #    reroll_7s   = row[2]  /  so convert with int() only if not None
            #    tier        = row[4]     same treatment
            #    leagues     = row[3] split on commas, each stripped, blanks dropped

            # 3. Parse the rules cell
            #    allowed, rule_lines = parse_special_rules(row[5])
            #    rule_names = every name from expand_rule_line(line) for each line

            # 4. Build the affiliation objects
            #    all_names = set(leagues) | set(rule_names)
            #    affiliations = [get_or_create(db, Affiliation, n) for n in all_names]

            # 5. Create or update the race
            #    race = get_or_create(db, Race, name,
            #                         tier=..., reroll_cost=..., reroll_cost_7s=...,
            #                         apothecary_allowed=allowed,
            #                         special_rule_text="\n".join(rule_lines) or None)

            # 6. Link them
            #    race.affiliations = affiliations

        db.commit()