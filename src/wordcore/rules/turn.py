def next_seat(players: tuple[int, ...], current: int) -> int:
    index = players.index(current)
    return players[(index + 1) % len(players)]
