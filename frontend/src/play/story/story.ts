import type { CompanyView, PositionView } from "../../api/views";
import { gathered } from "../seats/company";

export type StoryKind = "over" | "acting" | "gathering" | "watching";

export interface Story {
    readonly kind: StoryKind;
    readonly seats: readonly number[];
    readonly points: number | null;
    readonly mine: boolean;
}

export function storyFor(view: PositionView, company: CompanyView, mySeat: number | null): Story {
    if (view.phase === "game_over") {
        const top = Math.max(...view.players.map((seat) => view.scores[String(seat)] ?? 0));
        const winners = view.players.filter((seat) => (view.scores[String(seat)] ?? 0) === top);
        return { kind: "over", seats: winners, points: top, mine: mySeat !== null && winners.includes(mySeat) };
    }
    if (!gathered(company)) {
        return { kind: "gathering", seats: [], points: null, mine: false };
    }
    if (mySeat !== null && view.to_act.includes(mySeat)) {
        return { kind: "acting", seats: sorted(view.to_act), points: null, mine: true };
    }
    return { kind: "watching", seats: sorted(view.to_act), points: null, mine: false };
}

function sorted(seats: readonly number[]): readonly number[] {
    return [...seats].sort((left, right) => left - right);
}
