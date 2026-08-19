import type { GameHighlights, WordHighlight } from "../../api/highlights";

export type HighlightKind = "best" | "longest" | "both";

export interface HighlightRow {
    readonly kind: HighlightKind;
    readonly player: number;
    readonly word: string;
    readonly points: number;
}

export function highlightRows(highlights: GameHighlights): readonly HighlightRow[] {
    const best = highlights.best_word;
    const longest = highlights.longest_word;
    if (best === null || longest === null) {
        return [
            ...(best === null ? [] : [rowFor("best", best)]),
            ...(longest === null ? [] : [rowFor("longest", longest)]),
        ];
    }
    if (sameWord(best, longest)) {
        return [rowFor("both", best)];
    }
    return [rowFor("best", best), rowFor("longest", longest)];
}

function sameWord(one: WordHighlight, other: WordHighlight): boolean {
    return one.turn_number === other.turn_number && one.word === other.word;
}

function rowFor(kind: HighlightKind, highlight: WordHighlight): HighlightRow {
    return { kind, player: highlight.player, word: highlight.word, points: highlight.points };
}
