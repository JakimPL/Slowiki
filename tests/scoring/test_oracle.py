import hypothesis.strategies as st
from hypothesis import assume, given, settings
from tests.scoring.authored import authored_score

from wordcore.board.board import Board, Bonus, BonusKind
from wordcore.rules.scoring import score_move
from wordcore.rules.words import Placement, formed_words
from wordcore.tiles.tile import Tile

BONUSES = st.one_of(
    st.none(),
    st.just(Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=2)),
    st.just(Bonus(kind=BonusKind.WORD_MULTIPLIER, multiplier=3)),
    st.just(Bonus(kind=BonusKind.LETTER_MULTIPLIER, multiplier=2)),
    st.just(Bonus(kind=BonusKind.LETTER_MULTIPLIER, multiplier=3)),
    st.just(Bonus(kind=BonusKind.CATEGORY_MULTIPLIER, multiplier=3, category="red")),
)

TILES = st.builds(
    Tile,
    identifier=st.integers(min_value=0, max_value=10_000),
    letter=st.sampled_from(["a", "b", "c", "d", "e"]),
    value=st.integers(min_value=1, max_value=5),
    category=st.sampled_from(["yellow", "green", "red"]),
    blank=st.just(False),
)


@st.composite
def board_with_single_placement(draw):
    size = draw(st.integers(min_value=2, max_value=5))
    count = size * size
    bonuses = tuple(draw(BONUSES) for _ in range(count))
    tiles: list[Tile | None] = []
    occupied: list[int] = []
    for index in range(count):
        if len(occupied) < count // 2 and draw(st.booleans()):
            tiles.append(draw(TILES))
            occupied.append(index)
        else:
            tiles.append(None)
    assume(occupied)
    board = Board(size=size, bonuses=bonuses, tiles=tuple(tiles))
    neighbors = _adjacent_empty_cells(board, occupied)
    assume(neighbors)
    target = draw(st.sampled_from(neighbors))
    row, column = divmod(target, size)
    placement = Placement(tile=draw(TILES), row=row, column=column)
    return board, (placement,)


def _adjacent_empty_cells(board: Board, occupied: list[int]) -> list[int]:
    result: list[int] = []
    for index in occupied:
        row, column = divmod(index, board.size)
        for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_row = row + delta_row
            neighbor_column = column + delta_column
            if board.in_bounds(neighbor_row, neighbor_column):
                neighbor = board.index(neighbor_row, neighbor_column)
                if board.tiles[neighbor] is None and neighbor not in result:
                    result.append(neighbor)
    return result


@given(board_with_single_placement())
@settings(max_examples=200)
def test_oracle_matches_kernel(sample: tuple[Board, tuple[Placement, ...]]) -> None:
    board, placements = sample
    words = formed_words(board, placements)
    kernel = score_move(board, words, bingo=0)
    authored_words, authored_total = authored_score(board, placements)
    assert kernel.points == authored_total
    assert tuple(sorted((word.text, word.points) for word in kernel.words)) == authored_words
