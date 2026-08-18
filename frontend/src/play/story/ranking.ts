import type { PositionView } from "../../api/views";

export interface Ranked {
    readonly seat: number;
    readonly points: number;
    readonly place: number;
}

export function rankingOf(view: PositionView): readonly Ranked[] {
    const scored = view.players.map((seat) => ({ seat, points: view.scores[String(seat)] ?? 0 }));
    return [...scored]
        .sort((left, right) => right.points - left.points || left.seat - right.seat)
        .map((one) => ({ ...one, place: 1 + scored.filter((other) => other.points > one.points).length }));
}
