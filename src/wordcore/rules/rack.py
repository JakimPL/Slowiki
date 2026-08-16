from wordcore.exceptions import IllegalMove
from wordcore.positions.position import Position
from wordcore.tiles.tile import Tile


def rack_of(position: Position, player: int) -> tuple[Tile, ...]:
    rack = position.state.racks[player]
    if rack is None:
        raise IllegalMove("rack is hidden")
    return rack
