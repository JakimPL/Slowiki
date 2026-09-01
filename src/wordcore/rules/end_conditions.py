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
    rack_penalties: bool,
    going_out_award: bool,
    going_out_bonus: int,
) -> dict[int, int]:
    deductions = rack_deductions(position)
    scores = _standing_scores(position, deductions, rack_penalties=rack_penalties)
    if went_out is None:
        return scores

    earned = _finisher_earns(
        deductions,
        went_out,
        going_out_award=going_out_award,
        going_out_bonus=going_out_bonus,
    )
    return {**scores, went_out: scores[went_out] + earned}


def _standing_scores(
    position: Position,
    deductions: dict[int, int],
    *,
    rack_penalties: bool,
) -> dict[int, int]:
    if rack_penalties:
        return deducted_scores(position, deductions)

    return {seat: position.state.scores[seat] for seat in position.players}


def _finisher_earns(
    deductions: dict[int, int],
    went_out: int,
    *,
    going_out_award: bool,
    going_out_bonus: int,
) -> int:
    awarded = opponents_rack_total(deductions, went_out) if going_out_award else 0
    return awarded + going_out_bonus
