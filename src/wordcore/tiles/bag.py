import random

from wordcore.tiles.blank import BLANK_CATEGORY, BLANK_VALUE
from wordcore.tiles.tile import Tile
from wordcore.tiles.tileset import TileSet


def build_tiles(tiles: TileSet) -> tuple[Tile, ...]:
    built: list[Tile] = []
    identifier = 0
    for letter in tiles.letters:
        for _ in range(letter.count):
            built.append(
                Tile(
                    identifier=identifier,
                    letter=letter.symbol,
                    value=letter.value,
                    category=letter.category,
                    blank=False,
                )
            )
            identifier += 1

    for _ in range(tiles.blanks):
        built.append(
            Tile(
                identifier=identifier,
                letter="",
                value=BLANK_VALUE,
                category=BLANK_CATEGORY,
                blank=True,
            )
        )
        identifier += 1

    return tuple(built)


def shuffled_bag(tiles: TileSet, rng: random.Random) -> tuple[Tile, ...]:
    built = list(build_tiles(tiles))
    rng.shuffle(built)
    return tuple(built)


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
