import type { Board, Bonus, Tile } from "../../api/views";
import { combinedTiles } from "./board";
import type { FormedWord, Laid } from "./geometry";

export interface ScoredWord {
    readonly text: string;
    readonly points: number;
}

export function scoredWordsOf(
    board: Board,
    laid: readonly Laid[],
    words: readonly FormedWord[],
): readonly ScoredWord[] {
    const combined = combinedTiles(board, new Map(laid.map((piece) => [piece.cell, piece.tile])));
    const fresh = new Set(laid.map((piece) => piece.cell));
    return words.map((word) => ({
        text: word.text,
        points: wordPoints(board, combined, fresh, word),
    }));
}

function wordPoints(
    board: Board,
    combined: readonly (Tile | null)[],
    fresh: ReadonlySet<number>,
    word: FormedWord,
): number {
    let letters = 0;
    let multiplier = 1;
    for (const cell of word.cells) {
        const tile = combined[cell] ?? null;
        if (tile === null) {
            continue;
        }
        const bonus = fresh.has(cell) ? (board.bonuses[cell] ?? null) : null;
        letters += tile.value * letterBonus(bonus, tile);
        if (bonus !== null && bonus.kind === "word_multiplier") {
            multiplier *= bonus.multiplier;
        }
    }
    return letters * multiplier;
}

function letterBonus(bonus: Bonus | null, tile: Tile): number {
    if (bonus === null) {
        return 1;
    }
    if (bonus.kind === "letter_multiplier") {
        return bonus.multiplier;
    }
    if (bonus.kind === "category_multiplier" && bonus.category === tile.category) {
        return bonus.multiplier;
    }
    return 1;
}
