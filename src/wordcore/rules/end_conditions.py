from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of


def rack_deductions(position: Position) -> dict[int, int]:
    return {seat: sum(tile.value for tile in rack_of(position, seat)) for seat in position.players}


def deducted_scores(
    position: Position,
    deductions: dict[int, int],
) -> dict[int, int]:
    return {seat: position.state.scores[seat] - deductions[seat] for seat in position.players}


def opponents_rack_total(deductions: dict[int, int], went_out: int) -> int:
    return sum(value for seat, value in deductions.items() if seat != went_out)


def final_scores(
    position: Position,
    went_out: int | None,
    *,
    going_out_award: bool,
) -> dict[int, int]:
    deductions = rack_deductions(position)
    scores = deducted_scores(position, deductions)
    if went_out is None or not going_out_award:
        return scores

    return {**scores, went_out: scores[went_out] + opponents_rack_total(deductions, went_out)}
