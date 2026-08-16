from wordcore.exceptions import IllegalMove
from wordcore.moves.action import Exchange
from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of
from wordcore.tiles.tile import Tile


def validate_exchange(
    position: Position,
    player: int,
    exchange: Exchange,
    *,
    limit: int | None,
    min_bag: int,
) -> None:
    if not exchange.tile_ids:
        raise IllegalMove("exchange requires at least one tile")

    if len(set(exchange.tile_ids)) != len(exchange.tile_ids):
        raise IllegalMove("exchange lists a tile more than once")

    rack_ids = {tile.identifier for tile in rack_of(position, player)}
    if not set(exchange.tile_ids) <= rack_ids:
        raise IllegalMove("exchange tiles must be in the player's rack")

    if limit is not None and position.state.exchange_counts[player] >= limit:
        raise IllegalMove("exchange limit reached")

    if len(position.state.bag) < min_bag:
        raise IllegalMove("not enough tiles remain to exchange")


def apply_exchange(position: Position, player: int, exchange: Exchange) -> Position:
    rack = rack_of(position, player)
    exchanged = set(exchange.tile_ids)
    returned = _returned_tiles(rack, exchanged)
    kept = _kept_tiles(rack, exchanged)
    drawn = position.state.bag[: len(returned)]
    remaining = position.state.bag[len(returned) :]
    state = position.state
    new_state = state.model_copy(
        update={
            "racks": {**state.racks, player: kept + drawn},
            "bag": remaining + returned,
            "exchange_counts": {
                **state.exchange_counts,
                player: state.exchange_counts[player] + 1,
            },
        }
    )
    return position.model_copy(update={"state": new_state})


def _returned_tiles(rack: tuple[Tile, ...], exchanged: set[int]) -> tuple[Tile, ...]:
    return tuple(tile for tile in rack if tile.identifier in exchanged)


def _kept_tiles(rack: tuple[Tile, ...], exchanged: set[int]) -> tuple[Tile, ...]:
    return tuple(tile for tile in rack if tile.identifier not in exchanged)
