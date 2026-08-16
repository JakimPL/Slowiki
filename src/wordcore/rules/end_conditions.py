from wordcore.positions.position import Position
from wordcore.rules.rack import rack_of


def final_scores(position: Position, went_out: int | None) -> dict[int, int]:
    deductions = {
        seat: sum(tile.value for tile in rack_of(position, seat)) for seat in position.players
    }
    scores = dict(position.state.scores)
    for seat in position.players:
        scores[seat] -= deductions[seat]
    if went_out is not None:
        scores[went_out] += sum(deductions[seat] for seat in position.players if seat != went_out)
    return scores
