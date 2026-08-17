import { describe, expect, it } from "vitest";

import type { Draft } from "../src/play/draft";
import { prospectOf } from "../src/play/prospects";
import { FALLBACK_RULES } from "../src/play/rules";
import { aBoard, aTile } from "./positions";

const CENTER = 112;

const OPENING: Draft = [
    { cell: CENTER, tile: aTile({ identifier: 1, letter: "K", value: 2 }), letter: null },
    { cell: CENTER + 1, tile: aTile({ identifier: 2, letter: "O", value: 3 }), letter: null },
];

describe("prospectOf", () => {
    it("passes structural verdicts through with no words", () => {
        const prospect = prospectOf(
            aBoard(),
            [OPENING[0] ?? { cell: CENTER, tile: aTile(), letter: null }],
            FALLBACK_RULES,
        );
        expect(prospect.verdict).toBe("opening-short");
        expect(prospect.words).toEqual([]);
        expect(prospect.points).toBe(0);
    });

    it("totals the formed words", () => {
        const prospect = prospectOf(aBoard(), OPENING, FALLBACK_RULES);
        expect(prospect.verdict).toBe("playable");
        expect(prospect.words).toEqual([{ text: "KO", points: 5 }]);
        expect(prospect.points).toBe(5);
        expect(prospect.bingo).toBe(false);
    });

    it("adds the bingo bonus when the whole rack is laid", () => {
        const rules = { ...FALLBACK_RULES, rackSize: 2, bingoBonus: 50 };
        const prospect = prospectOf(aBoard(), OPENING, rules);
        expect(prospect.bingo).toBe(true);
        expect(prospect.points).toBe(55);
    });
});
