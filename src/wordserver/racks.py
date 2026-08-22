from collections.abc import Iterable

from wordcore.tiles.tile import Tile
from wordcore.views.projection import PositionView


class RackOrder:
    def __init__(self, seats: Iterable[int]) -> None:
        self._orders: dict[int, tuple[int, ...]] = {seat: () for seat in seats}

    def remember(self, seat: int, tile_ids: tuple[int, ...]) -> None:
        self._orders[seat] = tile_ids

    def arranged(self, view: PositionView, observer: int | None) -> PositionView:
        if observer is None:
            return view

        rack = view.racks.get(observer)
        if rack is None:
            return view

        return view.model_copy(
            update={"racks": {**view.racks, observer: self._ordered(rack, observer)}},
        )

    def _ordered(self, rack: tuple[Tile, ...], seat: int) -> tuple[Tile, ...]:
        remembered = self._orders[seat]
        held = {tile.identifier: tile for tile in rack}
        arranged = tuple(held[tile_id] for tile_id in remembered if tile_id in held)
        known = set(remembered)
        drawn = tuple(tile for tile in rack if tile.identifier not in known)
        return arranged + drawn
