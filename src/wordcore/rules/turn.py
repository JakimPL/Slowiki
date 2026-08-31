def next_seat(players: tuple[int, ...], current: int) -> int:
    index = players.index(current)
    return players[(index + 1) % len(players)]


def next_seat_among(players: tuple[int, ...], current: int, playing: frozenset[int]) -> int:
    index = players.index(current)
    for step in range(1, len(players) + 1):
        seat = players[(index + step) % len(players)]
        if seat in playing:
            return seat

    return next_seat(players, current)
