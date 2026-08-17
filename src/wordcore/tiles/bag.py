import random

from wordcore.tiles.tile import Tile, TilePreset


def build_tiles(preset: TilePreset) -> tuple[Tile, ...]:
    tiles: list[Tile] = []
    identifier = 0
    for letter in preset.letters:
        for _ in range(letter.count):
            tiles.append(
                Tile(
                    identifier=identifier,
                    letter=letter.symbol,
                    value=letter.value,
                    category=letter.category,
                    blank=False,
                )
            )
            identifier += 1

    for _ in range(preset.blanks):
        tiles.append(
            Tile(
                identifier=identifier,
                letter="",
                value=0,
                category="blank",
                blank=True,
            )
        )
        identifier += 1

    return tuple(tiles)


def shuffled_bag(preset: TilePreset, rng: random.Random) -> tuple[Tile, ...]:
    tiles = list(build_tiles(preset))
    rng.shuffle(tiles)
    return tuple(tiles)


def deal_racks(
    bag: tuple[Tile, ...], rack_sizes: dict[int, int | None]
) -> tuple[dict[int, tuple[Tile, ...] | None], tuple[Tile, ...]]:
    remaining = list(bag)
    racks: dict[int, tuple[Tile, ...] | None] = {}
    for seat, size in rack_sizes.items():
        if size is None:
            taken = tuple(remaining)
            remaining = []
        else:
            taken = tuple(remaining[:size])
            remaining = remaining[size:]
        racks[seat] = taken

    return racks, tuple(remaining)
