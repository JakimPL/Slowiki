import type { CompanyView, PositionView } from "../../api/views";

export type StoryKind = "over" | "acting" | "gathering" | "watching";

export interface Story {
    readonly kind: StoryKind;
    readonly seats: readonly number[];
    readonly points: number | null;
}

export function storyFor(view: PositionView, company: CompanyView, mySeat: number | null): Story {
    if (view.phase === "game_over") {
        const top = Math.max(...view.players.map((seat) => view.scores[String(seat)] ?? 0));
        const winners = view.players.filter((seat) => (view.scores[String(seat)] ?? 0) === top);
        return { kind: "over", seats: winners, points: top };
    }
    if (company.seats.some((seated) => !seated.claimed)) {
        return { kind: "gathering", seats: [], points: null };
    }
    if (mySeat !== null && view.to_act.includes(mySeat)) {
        return { kind: "acting", seats: sorted(view.to_act), points: null };
    }
    return { kind: "watching", seats: sorted(view.to_act), points: null };
}

function sorted(seats: readonly number[]): readonly number[] {
    return [...seats].sort((left, right) => left - right);
}
