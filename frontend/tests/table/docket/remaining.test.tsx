import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { remainingTally } from "../../../src/play/story/remaining";
import { RemainingTiles } from "../../../src/table/docket/RemainingTiles";
import { aBoard, aDescription, aTile } from "../../fixtures/positions";

describe("remainingTally", () => {
    it("subtracts the board and the own rack from the distribution", () => {
        const description = aDescription({ distribution: { A: 9, K: 3 }, blanks: 2 });
        const board = aBoard({
            0: aTile({ identifier: 1, letter: "A" }),
            1: aTile({ identifier: 2, letter: "", value: 0, category: "blank", blank: true }),
        });
        const rack = [aTile({ identifier: 3, letter: "K" }), aTile({ identifier: 4, letter: "A" })];
        const tally = remainingTally(description, board, rack);
        expect(tally.letters).toEqual([
            { symbol: "A", category: "yellow", count: 7 },
            { symbol: "K", category: "green", count: 2 },
        ]);
        expect(tally.blanks).toBe(1);
    });

    it("counts nothing below zero and handles a hidden rack", () => {
        const description = aDescription({ distribution: { A: 1, K: 0 }, blanks: 0 });
        const board = aBoard({
            0: aTile({ identifier: 1, letter: "A" }),
            1: aTile({ identifier: 2, letter: "A" }),
        });
        const tally = remainingTally(description, board, null);
        expect(tally.letters).toEqual([
            { symbol: "A", category: "yellow", count: 0 },
            { symbol: "K", category: "green", count: 0 },
        ]);
        expect(tally.blanks).toBe(0);
    });
});

describe("RemainingTiles", () => {
    it("lists every letter with its count and dims the spent ones", () => {
        const tally = {
            letters: [
                { symbol: "A", category: "yellow", count: 7 },
                { symbol: "K", category: "red", count: 0 },
            ],
            blanks: 2,
        };
        const markup = renderToStaticMarkup(<RemainingTiles tally={tally} />);
        expect(markup).toContain("Remaining tiles");
        expect(markup).toContain(">A</b>");
        expect(markup).toContain(">7</span>");
        expect(markup).toContain('data-spent="true"');
        expect(markup).toContain(">◇</b>");
        expect(markup).toContain("--face:var(--tile-face-yellow, var(--tile-face))");
    });
});
