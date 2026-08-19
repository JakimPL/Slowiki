import type { PositionView } from "../../api/views";

export interface Ranked {
    readonly seat: number;
    readonly points: number;
    readonly place: number;
    readonly podium: number | null;
}

const PODIUM_SEATS = 4;
const PODIUM_STEPS = 3;
const WINNER_ALONE = 1;

export function rankingOf(view: PositionView): readonly Ranked[] {
    const steps = view.players.length >= PODIUM_SEATS ? PODIUM_STEPS : WINNER_ALONE;
    const scored = view.players.map((seat) => ({ seat, points: view.scores[String(seat)] ?? 0 }));
    return [...scored]
        .sort((left, right) => right.points - left.points || left.seat - right.seat)
        .map((one) => {
            const place = 1 + scored.filter((other) => other.points > one.points).length;
            return { ...one, place, podium: place <= steps ? place : null };
        });
}
