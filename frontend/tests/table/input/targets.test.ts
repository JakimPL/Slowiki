import { describe, expect, it } from "vitest";

import type { TargetMap } from "../../../src/table/input/targets";
import { landingAt } from "../../../src/table/input/targets";

const MAP: TargetMap = {
    size: 15,
    board: { left: 0, top: 0, width: 300, height: 300 },
    viewport: { left: 0, top: 0, width: 300, height: 300 },
    rack: { left: 0, top: 320, width: 300, height: 50 },
    rackSlots: [
        { id: 1, rect: { left: 10, top: 320, width: 40, height: 50 } },
        { id: 2, rect: { left: 60, top: 320, width: 40, height: 50 } },
    ],
    tray: { left: 0, top: 380, width: 300, height: 50 },
    traySlots: [{ id: 9, rect: { left: 10, top: 380, width: 40, height: 50 } }],
};

describe("landingAt", () => {
    it("maps board points onto cells by grid arithmetic", () => {
        expect(landingAt(MAP, 10, 10)).toEqual({ kind: "cell", cell: 0 });
        expect(landingAt(MAP, 150, 150)).toEqual({ kind: "cell", cell: 7 * 15 + 7 });
        expect(landingAt(MAP, 299, 299)).toEqual({ kind: "cell", cell: 224 });
    });

    it("finds the rack insertion point by tile midpoints", () => {
        expect(landingAt(MAP, 5, 340)).toEqual({ kind: "rack", before: 1 });
        expect(landingAt(MAP, 55, 340)).toEqual({ kind: "rack", before: 2 });
        expect(landingAt(MAP, 200, 340)).toEqual({ kind: "rack", before: null });
    });

    it("targets the tray row and the void beyond", () => {
        expect(landingAt(MAP, 5, 400)).toEqual({ kind: "tray", before: 9 });
        expect(landingAt(MAP, 200, 400)).toEqual({ kind: "tray", before: null });
        expect(landingAt(MAP, 200, 500)).toBeNull();
    });
});

describe("landingAt over a magnified board", () => {
    const MAGNIFIED: TargetMap = { ...MAP, board: { left: -300, top: -300, width: 900, height: 900 } };

    it("maps a point the player can see onto the square under it", () => {
        expect(landingAt(MAGNIFIED, 150, 150)).toEqual({ kind: "cell", cell: 7 * 15 + 7 });
    });

    it("leaves the rack reachable under the magnified board's own rectangle", () => {
        expect(landingAt(MAGNIFIED, 5, 340)).toEqual({ kind: "rack", before: 1 });
    });

    it("counts the clipped-away board as the void", () => {
        expect(landingAt(MAGNIFIED, 500, 500)).toBeNull();
    });
});
