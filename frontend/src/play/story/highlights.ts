import type { GameHighlights } from "../../api/highlights";
import type { ScoredWord } from "../board/scoring";

export type HighlightKind = "best" | "longest" | "both";

export interface HighlightRow {
    readonly kind: HighlightKind;
    readonly player: number;
    readonly words: readonly ScoredWord[];
    readonly points: number;
}

const SOLE_WORD = 1;

export function highlightRows(highlights: GameHighlights): readonly HighlightRow[] {
    const best = highlights.best_play;
    const longest = highlights.longest_word;
    if (best === null || longest === null) {
        return [...(best === null ? [] : [playRow("best", best)]), ...(longest === null ? [] : [wordRow(longest)])];
    }
    if (best.turn_number === longest.turn_number && best.words.length === SOLE_WORD) {
        return [playRow("both", best)];
    }
    return [playRow("best", best), wordRow(longest)];
}

function playRow(kind: HighlightKind, play: NonNullable<GameHighlights["best_play"]>): HighlightRow {
    return { kind, player: play.player, words: play.words, points: play.points };
}

function wordRow(word: NonNullable<GameHighlights["longest_word"]>): HighlightRow {
    return {
        kind: "longest",
        player: word.player,
        words: [{ text: word.word, points: word.points }],
        points: word.points,
    };
}
