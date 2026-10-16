import re
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.races import Race
from app.models.positions import Position
from scripts.common import load_sheet, upsert

KEY_RE = re.compile(r"^(.*?)(\d+|J)$")
ACCESS = ["General", "Agility", "Strength", "Passing", "Mutation", "Devious"]


def stat(value):
    return int(str(value).rstrip("+"))


def clean_name(raw):
    name = re.sub(r"\s*\([^)]*\)", "", str(raw))
    return re.sub(r"\s+", " ", name).strip(" *")


def access(cells, marker):
    found = [cat for cat, c in zip(ACCESS, cells) if c == marker]
    return ", ".join(found) or None


def main():
    ws = load_sheet("Positions")
    processed = 0

    with SessionLocal() as db:
        races = {r.name: r for r in db.scalars(select(Race))}

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            key = str(row[0]).strip()
            if "(S2)" in key:
                continue

            match = KEY_RE.match(key)
            race = races.get(match.group(1).strip()) if match else None
            if race is None:
                raise ValueError(f"No race found for key {key!r}")

            name = clean_name(row[2])
            if not name:
                continue

            upsert(
                db,
                Position,
                {"race_id": race.id, "name": name},
                max_allowed=int(row[1]) if row[1] is not None else 0,
                movement=stat(row[3]),
                strength=stat(row[4]),
                agility=stat(row[5]),
                passing=stat(row[6]),
                armor=stat(row[7]),
                skill_list=str(row[8]).strip() if row[8] else None,
                cost=int(row[9]) if row[9] is not None else 0,
                primary_access=access(row[10:16], "Y"),
                secondary_access=access(row[10:16], "D"),
            )
            processed += 1

        db.commit()

    print(f"Done. {processed} positions processed.")


if __name__ == "__main__":
    main()