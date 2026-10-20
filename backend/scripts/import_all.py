from scripts import (
    import_skills, import_races, import_positions, import_star_players,
    import_inducements, import_mercenaries, import_dungeon_bowl,
)

STEPS = [
    import_skills, import_races, import_positions, import_star_players,
    import_inducements, import_mercenaries, import_dungeon_bowl,
]


def main():
    for step in STEPS:
        print(f"--> {step.__name__}")
        step.main()


if __name__ == "__main__":
    main()