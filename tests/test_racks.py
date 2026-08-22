from wordcore.board.board import Board
from wordcore.positions.position import Position
from wordcore.states.state import Phase, WordState
from wordcore.tiles.tile import Tile
from wordcore.views.projection import PositionView, project
from wordserver.racks import RackOrder

SEATS = (0, 1)


def a_tile(identifier: int) -> Tile:
    return Tile(identifier=identifier, letter="A", value=1, category="yellow", blank=False)


def a_view(racks: dict[int, tuple[Tile, ...]], observer: int) -> PositionView:
    state = WordState(
        phase=Phase.TURN,
        to_act=frozenset({0}),
        racks=racks,
        bag=(),
        scores={seat: 0 for seat in SEATS},
        exchange_counts={seat: 0 for seat in SEATS},
        consecutive_passes=0,
        premoves={},
        turn_number=0,
    )
    board = Board(size=1, bonuses=(None,), tiles=(None,))
    return project(Position(board=board, state=state, players=SEATS), observer)


def identifiers(view: PositionView, seat: int) -> list[int]:
    rack = view.racks[seat]
    assert rack is not None
    return [tile.identifier for tile in rack]


def test_a_served_rack_keeps_its_order_until_a_seat_asks() -> None:
    orders = RackOrder(SEATS)
    view = a_view({0: (a_tile(1), a_tile(2), a_tile(3)), 1: ()}, observer=0)
    assert identifiers(orders.arranged(view, 0), 0) == [1, 2, 3]


def test_a_remembered_order_arranges_the_seat_that_asked_for_it() -> None:
    orders = RackOrder(SEATS)
    orders.remember(0, (3, 1, 2))
    view = a_view({0: (a_tile(1), a_tile(2), a_tile(3)), 1: ()}, observer=0)
    assert identifiers(orders.arranged(view, 0), 0) == [3, 1, 2]


def test_freshly_drawn_tiles_stand_at_the_end() -> None:
    orders = RackOrder(SEATS)
    orders.remember(0, (3, 1, 2))
    view = a_view({0: (a_tile(3), a_tile(7), a_tile(1), a_tile(8)), 1: ()}, observer=0)
    assert identifiers(orders.arranged(view, 0), 0) == [3, 1, 7, 8]


def test_a_hidden_rack_reaches_the_observer_untouched() -> None:
    orders = RackOrder(SEATS)
    orders.remember(1, (2, 1))
    view = a_view({0: (a_tile(1),), 1: (a_tile(1), a_tile(2))}, observer=0)
    arranged = orders.arranged(view, 0)
    assert arranged.racks[1] is None
    assert identifiers(arranged, 0) == [1]


def test_a_watcher_reads_the_position_as_it_stands() -> None:
    orders = RackOrder(SEATS)
    orders.remember(0, (2, 1))
    view = a_view({0: (a_tile(1), a_tile(2)), 1: ()}, observer=None)
    assert orders.arranged(view, None) is view
