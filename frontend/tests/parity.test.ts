import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { Board, Bonus, Tile } from "../src/api/views";
import type { Laid } from "../src/play/geometry";
import { formationOf } from "../src/play/geometry";
import { scoredWordsOf } from "../src/play/scoring";

interface FixtureTile {
    readonly index: number;
    readonly identifier: number;
    readonly letter: string;
    readonly value: number;
    readonly category: string;
    readonly blank: boolean;
}

interface FixtureBonus {
    readonly index: number;
    readonly kind: Bonus["kind"];
    readonly multiplier: number;
    readonly category: string | null;
}

interface FixtureCase {
    readonly name: string;
    readonly size: number;
    readonly bonuses: readonly FixtureBonus[];
    readonly tiles: readonly FixtureTile[];
    readonly placements: readonly FixtureTile[];
    readonly words: readonly (readonly [string, number])[];
    readonly total: number;
}

const fixture = JSON.parse(
    readFileSync(new URL("./parity/scoring.json", import.meta.url), "utf-8"),
) as { cases: readonly FixtureCase[] };

function boardOf(parityCase: FixtureCase): Board {
    const cells = parityCase.size * parityCase.size;
    const bonuses: (Bonus | null)[] = Array.from({ length: cells }, () => null);
    for (const bonus of parityCase.bonuses) {
        bonuses[bonus.index] = { kind: bonus.kind, multiplier: bonus.multiplier, category: bonus.category };
    }
    const tiles: (Tile | null)[] = Array.from({ length: cells }, () => null);
    for (const placed of parityCase.tiles) {
        tiles[placed.index] = tileOf(placed);
    }
    return { size: parityCase.size, bonuses, tiles };
}

function tileOf(placed: FixtureTile): Tile {
    return {
        identifier: placed.identifier,
        letter: placed.letter,
        value: placed.value,
        category: placed.category,
        blank: placed.blank,
    };
}

function sortedPairs(pairs: readonly (readonly [string, number])[]): readonly (readonly [string, number])[] {
    return [...pairs].sort((left, right) => {
        if (left[0] !== right[0]) {
            return left[0] < right[0] ? -1 : 1;
        }
        return left[1] - right[1];
    });
}

describe("scoring parity with the Python oracle", () => {
    for (const parityCase of fixture.cases) {
        it(`matches ${parityCase.name}`, () => {
            const board = boardOf(parityCase);
            const laid: readonly Laid[] = parityCase.placements.map((placed) => ({
                cell: placed.index,
                tile: tileOf(placed),
            }));
            const formation = formationOf(board, laid);
            expect(formation.verdict).toBe("playable");
            const scored = scoredWordsOf(board, laid, formation.words);
            const pairs = sortedPairs(scored.map((word) => [word.text, word.points] as const));
            expect(pairs).toEqual(sortedPairs(parityCase.words));
            expect(scored.reduce((sum, word) => sum + word.points, 0)).toBe(parityCase.total);
        });
    }
});
