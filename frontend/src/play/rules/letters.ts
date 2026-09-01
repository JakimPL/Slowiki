import type { AlphabetPreset, DistributionPreset } from "../../api/tables";
import type { LetterAdjustments } from "./changes";

const UNKNOWN_CATEGORY = "standard";

export interface LetterRow {
    readonly symbol: string;
    readonly value: number;
    readonly category: string;
    readonly count: number;
    readonly changed: boolean;
}

export function letterRows(
    alphabet: AlphabetPreset,
    distribution: DistributionPreset,
    adjustments: LetterAdjustments,
): readonly LetterRow[] {
    const classes = classesBySymbol(alphabet);
    const counts = countsBySymbol(distribution);
    const ordered = alphabet.order.map((symbol) =>
        adjusted(standardRow(symbol, classes.get(symbol), counts.get(symbol)), adjustments[symbol]),
    );
    return [...ordered, ...addedRows(alphabet, adjustments)];
}

export function bagTotal(rows: readonly LetterRow[], blanks: number): number {
    return rows.reduce((total, row) => total + row.count, blanks);
}

export function categoriesOf(rows: readonly LetterRow[]): readonly string[] {
    return [...new Set(rows.map((row) => row.category))];
}

function classesBySymbol(alphabet: AlphabetPreset): ReadonlyMap<string, AlphabetClass> {
    const held = new Map<string, AlphabetClass>();
    for (const letters of alphabet.classes) {
        for (const symbol of letters.letters) {
            held.set(symbol, { value: letters.value, category: letters.category });
        }
    }
    return held;
}

function countsBySymbol(distribution: DistributionPreset): ReadonlyMap<string, number> {
    const held = new Map<string, number>();
    for (const [count, symbols] of Object.entries(distribution.counts)) {
        for (const symbol of symbols) {
            held.set(symbol, Number(count));
        }
    }
    return held;
}

interface AlphabetClass {
    readonly value: number;
    readonly category: string;
}

function standardRow(symbol: string, letters: AlphabetClass | undefined, count: number | undefined): LetterRow {
    return {
        symbol,
        value: letters?.value ?? 0,
        category: letters?.category ?? UNKNOWN_CATEGORY,
        count: count ?? 0,
        changed: false,
    };
}

function adjusted(row: LetterRow, adjustment: LetterAdjustments[string] | undefined): LetterRow {
    if (adjustment === undefined) {
        return row;
    }
    return {
        symbol: row.symbol,
        value: adjustment.value ?? row.value,
        category: adjustment.category ?? row.category,
        count: adjustment.count ?? row.count,
        changed: true,
    };
}

function addedRows(alphabet: AlphabetPreset, adjustments: LetterAdjustments): readonly LetterRow[] {
    const ordered = new Set(alphabet.order);
    return Object.entries(adjustments)
        .filter(([symbol]) => !ordered.has(symbol))
        .map(([symbol, adjustment]) => ({
            symbol,
            value: adjustment.value ?? 0,
            category: adjustment.category ?? UNKNOWN_CATEGORY,
            count: adjustment.count ?? 0,
            changed: true,
        }));
}
