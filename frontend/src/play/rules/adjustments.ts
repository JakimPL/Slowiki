import type { LetterAdjustments } from "./changes";
import type { LetterRow } from "./letters";

export interface LetterChange {
    readonly value?: number | null;
    readonly category?: string | null;
    readonly count?: number | null;
}

export function withLetter(
    adjustments: LetterAdjustments,
    standard: readonly LetterRow[],
    symbol: string,
    change: LetterChange,
): LetterAdjustments {
    const row = standard.find((held) => held.symbol === symbol);
    if (row === undefined) {
        return adjustments;
    }
    const asked = { ...adjustments[symbol], ...change };
    const kept = apart(asked, row);
    return kept === null ? without(adjustments, symbol) : { ...adjustments, [symbol]: kept };
}

export function withCategory(
    adjustments: LetterAdjustments,
    standard: readonly LetterRow[],
    category: string,
    value: number,
): LetterAdjustments {
    return standard
        .filter((row) => row.category === category)
        .reduce((held, row) => withLetter(held, standard, row.symbol, { value }), adjustments);
}

function apart(asked: LetterChange, row: LetterRow): LetterChange | null {
    const value = asked.value ?? null;
    const category = asked.category ?? null;
    const count = asked.count ?? null;
    const kept: LetterChange = {
        ...(value !== null && value !== row.value ? { value } : {}),
        ...(category !== null && category !== row.category ? { category } : {}),
        ...(count !== null && count !== row.count ? { count } : {}),
    };
    return Object.keys(kept).length === 0 ? null : kept;
}

function without(adjustments: LetterAdjustments, symbol: string): LetterAdjustments {
    let kept: LetterAdjustments = {};
    for (const [held, adjustment] of Object.entries(adjustments)) {
        if (held !== symbol) {
            kept = { ...kept, [held]: adjustment };
        }
    }
    return kept;
}
