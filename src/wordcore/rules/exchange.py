from wordcore.exceptions import IllegalMove
from wordcore.moves.action import Exchange
from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of


def validate_exchange(
    position: Position, player: int, exchange: Exchange, limit: int | None, min_bag: int
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
    returned = [tile for tile in rack if tile.identifier in exchanged]
    kept = [tile for tile in rack if tile.identifier not in exchanged]
    bag = list(position.state.bag)
    drawn = bag[: len(returned)]
    new_bag = tuple(bag[len(returned) :] + returned)
    new_rack = tuple(kept + drawn)
    state = position.state
    new_state = state.model_copy(
        update={
            "racks": {**state.racks, player: new_rack},
            "bag": new_bag,
            "exchange_counts": {**state.exchange_counts, player: state.exchange_counts[player] + 1},
        }
    )
    return position.model_copy(update={"state": new_state})
