import re
from app.core.database import SessionLocal
from app.models.dungeon_bowl_races import db_Race                 
from app.models.dungeon_bowl_positions import db_position
from scripts.common import load_sheet, get_or_create, access

KEY_RE = re.compile(r"^(.*?)(\d+|J)$")       # "College of Beasts1" to "College of Beasts"
MAX_RE = re.compile(r"^([A-Za-z]+)(\d+)$")    # "LM16" to ("LM", "16")


def clean_name(raw):
    name = re.sub(r"\s*\([^)]*\)", "", str(raw))
    return re.sub(r"\s+", " ", name).strip(" *")


def main():
    ws = load_sheet("DBowl Positions")
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]

    with SessionLocal() as db:
        # colleges
        colleges = {}
        for row in rows:
            college = KEY_RE.match(str(row[0]).strip()).group(1).strip()
            if college not in colleges:
                colleges[college] = get_or_create(db, db_Race, college)

        # positions
        for row in rows:
            college = KEY_RE.match(str(row[0]).strip()).group(1).strip()
            role, limit = MAX_RE.match(str(row[1]).strip()).groups()

            get_or_create(
                db,
                db_position,
                clean_name(row[2]),
                db_race_id=colleges[college].id,
                role_code=role,
                max_allowed=int(limit),
                movement=int(row[3]),
                strength=int(row[4]),
                agility=int(row[5]),
                passing=int(row[6]),
                armor=int(row[7]),
                skill_list=str(row[8]).strip() if row[8] else None,
                cost=int(row[9]),
                primary_access=access(row[10:16], "Y"),
                secondary_access=access(row[10:16], "D"),
            )

        db.commit()

    print(f"Done. {len(colleges)} colleges and {len(rows)} positions processed.")


if __name__ == "__main__":
    main()