import { describe, expect, it } from "vitest";

import type { RowTarget, TargetMap } from "../../../src/table/input/targets";
import { landingAt, overBoard } from "../../../src/table/input/targets";

const RACK: RowTarget = {
    region: "rack",
    rect: { left: 0, top: 320, width: 300, height: 50 },
    slots: [
        { id: 1, rect: { left: 10, top: 324, width: 40, height: 42 } },
        { id: 2, rect: { left: 60, top: 324, width: 40, height: 42 } },
    ],
};

const TRAY: RowTarget = {
    region: "tray",
    rect: { left: 0, top: 380, width: 300, height: 50 },
    slots: [{ id: 9, rect: { left: 10, top: 384, width: 40, height: 42 } }],
};

const MAP: TargetMap = {
    size: 15,
    board: { left: 0, top: 0, width: 300, height: 300 },
    viewport: { left: 0, top: 0, width: 300, height: 300 },
    rows: [RACK, TRAY],
};

describe("landingAt", () => {
    it("maps board points onto cells by grid arithmetic", () => {
        expect(landingAt(MAP, 10, 10)).toEqual({ kind: "cell", cell: 0 });
        expect(landingAt(MAP, 150, 150)).toEqual({ kind: "cell", cell: 7 * 15 + 7 });
        expect(landingAt(MAP, 299, 299)).toEqual({ kind: "cell", cell: 224 });
    });

    it("takes the rack gap nearest the tile", () => {
        expect(landingAt(MAP, 5, 345)).toEqual({ kind: "rack", before: 1 });
        expect(landingAt(MAP, 29, 345)).toEqual({ kind: "rack", before: 1 });
        expect(landingAt(MAP, 31, 345)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(MAP, 79, 345)).toEqual({ kind: "rack", before: 2 });
    });

    it("reaches the end of the row by aiming past the last tile", () => {
        expect(landingAt(MAP, 81, 345)).toEqual({ kind: "rack", before: null });
        expect(landingAt(MAP, 200, 345)).toEqual({ kind: "rack", before: null });
    });

    it("keeps the gap a drop was aimed at when the aim misses the tiles", () => {
        expect(landingAt(MAP, 55, 321)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(MAP, 55, 369)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(MAP, 200, 321)).toEqual({ kind: "rack", before: null });
    });

    it("lets a row answer for a point just short of it", () => {
        expect(landingAt(MAP, 55, 312)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(MAP, 5, 438)).toEqual({ kind: "tray", before: 9 });
    });

    it("divides the space between the rack and the tray", () => {
        expect(landingAt(MAP, 5, 373)).toEqual({ kind: "rack", before: 1 });
        expect(landingAt(MAP, 5, 377)).toEqual({ kind: "tray", before: 9 });
    });

    it("targets the tray row and the void beyond", () => {
        expect(landingAt(MAP, 5, 400)).toEqual({ kind: "tray", before: 9 });
        expect(landingAt(MAP, 200, 400)).toEqual({ kind: "tray", before: null });
        expect(landingAt(MAP, 200, 500)).toBeNull();
        expect(landingAt(MAP, 200, 305)).toBeNull();
    });

    it("takes an empty row at its end", () => {
        const empty: TargetMap = { ...MAP, rows: [{ ...RACK, slots: [] }] };
        expect(landingAt(empty, 55, 345)).toEqual({ kind: "rack", before: null });
    });
});

describe("landingAt over a wrapped rack", () => {
    const WRAPPED: TargetMap = {
        ...MAP,
        rows: [
            {
                region: "rack",
                rect: { left: 0, top: 320, width: 300, height: 100 },
                slots: [
                    { id: 1, rect: { left: 10, top: 324, width: 40, height: 42 } },
                    { id: 2, rect: { left: 60, top: 324, width: 40, height: 42 } },
                    { id: 3, rect: { left: 10, top: 372, width: 40, height: 42 } },
                    { id: 4, rect: { left: 60, top: 372, width: 40, height: 42 } },
                ],
            },
        ],
    };

    it("answers with a gap from the band the aim is nearest to", () => {
        expect(landingAt(WRAPPED, 55, 345)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(WRAPPED, 55, 393)).toEqual({ kind: "rack", before: 4 });
    });

    it("reads the space between the bands as the nearer band", () => {
        expect(landingAt(WRAPPED, 55, 367)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(WRAPPED, 55, 371)).toEqual({ kind: "rack", before: 4 });
    });

    it("takes the end of the row from past the last tile of the last band", () => {
        expect(landingAt(WRAPPED, 200, 393)).toEqual({ kind: "rack", before: null });
    });
});

describe("landingAt over a magnified board", () => {
    const MAGNIFIED: TargetMap = { ...MAP, board: { left: -300, top: -300, width: 900, height: 900 } };

    it("maps a point the player can see onto the square under it", () => {
        expect(landingAt(MAGNIFIED, 150, 150)).toEqual({ kind: "cell", cell: 7 * 15 + 7 });
    });

    it("leaves the rack reachable under the magnified board's own rectangle", () => {
        expect(landingAt(MAGNIFIED, 5, 345)).toEqual({ kind: "rack", before: 1 });
    });

    it("counts the clipped-away board as the void", () => {
        expect(landingAt(MAGNIFIED, 500, 500)).toBeNull();
    });
});

describe("overBoard", () => {
    it("holds the board's own geometry apart from the rows", () => {
        expect(overBoard(MAP, 150, 150)).toBe(true);
        expect(overBoard(MAP, 150, 345)).toBe(false);
    });
});
