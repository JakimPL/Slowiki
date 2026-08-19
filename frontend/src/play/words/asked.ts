import type { ScoredWord } from "../board/scoring";
import type { WordStatus } from "./feedback";

export interface AskedWord {
    readonly text: string;
    readonly points: number | null;
    readonly status: WordStatus;
}

export function askedPlayed(word: ScoredWord): AskedWord {
    return { text: word.text, points: word.points, status: "standing" };
}

export function askedStanding(word: string): AskedWord {
    return { text: word, points: null, status: "standing" };
}
