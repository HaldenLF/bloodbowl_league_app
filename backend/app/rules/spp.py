from app.models.players import Player

COMPLETION = 1
TOUCHDOWN = 3
INTERCEPTION = 2
CASUALTY = 2
MVP = 4


def star_player_points(player: Player) -> int:
    return (
        player.completions * COMPLETION
        + player.touchdowns * TOUCHDOWN
        + player.interceptions * INTERCEPTION
        + player.casualties * CASUALTY
        + player.mvps * MVP
    )
