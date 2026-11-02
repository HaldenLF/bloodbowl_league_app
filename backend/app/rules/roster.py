from app.models.positions import Position

MIN_PLAYERS_FOR_A_GAME = 11
SHIRT_NUMBERS = range(1, 100)


def lowest_free_number(taken: set[int]) -> int | None:
    return next((number for number in SHIRT_NUMBERS if number not in taken), None)


def is_journeyman(position: Position) -> bool:
    return position.name.lower().startswith("journeyman")


def journeymen_allowed(available_players: int) -> bool:
    return available_players < MIN_PLAYERS_FOR_A_GAME
