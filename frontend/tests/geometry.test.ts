import { describe, expect, it } from "vitest";

import { cellIndex, centerIndex } from "../src/play/board";
import type { Laid } from "../src/play/geometry";
import { formationOf } from "../src/play/geometry";
import { aBoard, aTile } from "./positions";

const SIZE = 15;
const CENTER = centerIndex(SIZE);

function laid(cell: number, letter: string, identifier: number): Laid {
    return { cell, tile: aTile({ identifier, letter }) };
}

describe("formationOf", () => {
    it("reports an empty desk", () => {
        const formation = formationOf(aBoard(), []);
        expect(formation).toEqual({ verdict: "empty", words: [] });
    });

    it("rejects a single-tile opening", () => {
        const formation = formationOf(aBoard(), [laid(CENTER, "A", 1)]);
        expect(formation.verdict).toBe("opening-short");
    });

    it("requires the opening to cover the center", () => {
        const formation = formationOf(aBoard(), [laid(0, "A", 1), laid(1, "B", 2)]);
        expect(formation.verdict).toBe("off-center");
    });

    it("accepts an opening word across the center", () => {
        const formation = formationOf(aBoard(), [laid(CENTER, "K", 1), laid(CENTER + 1, "O", 2)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([{ cells: [CENTER, CENTER + 1], text: "KO" }]);
    });

    it("accepts a vertical opening through the center", () => {
        const formation = formationOf(aBoard(), [laid(CENTER - SIZE, "K", 1), laid(CENTER, "O", 2)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([{ cells: [CENTER - SIZE, CENTER], text: "KO" }]);
    });

    it("flags a gap in the laid line", () => {
        const formation = formationOf(aBoard(), [laid(CENTER, "K", 1), laid(CENTER + 2, "O", 2)]);
        expect(formation.verdict).toBe("gapped");
    });

    it("flags tiles scattered across rows and columns", () => {
        const formation = formationOf(aBoard(), [laid(CENTER, "K", 1), laid(CENTER + SIZE + 1, "O", 2)]);
        expect(formation.verdict).toBe("scattered");
    });

    it("flags a play that touches nothing on a started board", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "A" }) });
        const formation = formationOf(board, [laid(0, "B", 2), laid(1, "C", 3)]);
        expect(formation.verdict).toBe("detached");
    });

    it("extends an existing word with a single tile", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "A" }) });
        const formation = formationOf(board, [laid(CENTER + 1, "B", 2)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([{ cells: [CENTER, CENTER + 1], text: "AB" }]);
    });

    it("forms both lines around a single bridging tile", () => {
        const left = cellIndex(SIZE, 7, 6);
        const above = cellIndex(SIZE, 6, 7);
        const bridge = cellIndex(SIZE, 7, 7);
        const board = aBoard({
            [left]: aTile({ letter: "A" }),
            [above]: aTile({ letter: "O", identifier: 2 }),
        });
        const formation = formationOf(board, [laid(bridge, "T", 3)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([
            { cells: [left, bridge], text: "AT" },
            { cells: [above, bridge], text: "OT" },
        ]);
    });

    it("collects the main word and every cross word", () => {
        const boardA = cellIndex(SIZE, 7, 7);
        const boardB = cellIndex(SIZE, 8, 7);
        const board = aBoard({
            [boardA]: aTile({ letter: "A" }),
            [boardB]: aTile({ letter: "B", identifier: 2 }),
        });
        const laidC = cellIndex(SIZE, 7, 8);
        const laidD = cellIndex(SIZE, 8, 8);
        const formation = formationOf(board, [laid(laidC, "C", 3), laid(laidD, "D", 4)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([
            { cells: [laidC, laidD], text: "CD" },
            { cells: [boardA, laidC], text: "AC" },
            { cells: [boardB, laidD], text: "BD" },
        ]);
    });

    it("stretches the main word over existing tiles between placements", () => {
        const middle = cellIndex(SIZE, 7, 7);
        const board = aBoard({ [middle]: aTile({ letter: "O" }) });
        const formation = formationOf(board, [laid(middle - 1, "K", 2), laid(middle + 1, "T", 3)]);
        expect(formation.verdict).toBe("playable");
        expect(formation.words).toEqual([{ cells: [middle - 1, middle, middle + 1], text: "KOT" }]);
    });
});
