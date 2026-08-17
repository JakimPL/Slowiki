import { describe, expect, it } from "vitest";

import { CARRY_THRESHOLD, isCarry } from "../src/table/dragging";
import type { TargetMap } from "../src/table/targets";
import { resolveTarget } from "../src/table/targets";

const MAP: TargetMap = {
    size: 15,
    board: { left: 0, top: 0, width: 300, height: 300 },
    rack: { left: 0, top: 320, width: 300, height: 50 },
    rackSlots: [
        { id: 1, rect: { left: 10, top: 320, width: 40, height: 50 } },
        { id: 2, rect: { left: 60, top: 320, width: 40, height: 50 } },
    ],
    tray: { left: 0, top: 380, width: 300, height: 50 },
    traySlots: [{ id: 9, rect: { left: 10, top: 380, width: 40, height: 50 } }],
};

describe("resolveTarget", () => {
    it("maps board points onto cells by grid arithmetic", () => {
        expect(resolveTarget(MAP, 10, 10)).toEqual({ kind: "cell", cell: 0 });
        expect(resolveTarget(MAP, 150, 150)).toEqual({ kind: "cell", cell: 7 * 15 + 7 });
        expect(resolveTarget(MAP, 299, 299)).toEqual({ kind: "cell", cell: 224 });
    });

    it("finds the rack insertion point by tile midpoints", () => {
        expect(resolveTarget(MAP, 5, 340)).toEqual({ kind: "rack", before: 1 });
        expect(resolveTarget(MAP, 55, 340)).toEqual({ kind: "rack", before: 2 });
        expect(resolveTarget(MAP, 200, 340)).toEqual({ kind: "rack", before: null });
    });

    it("targets the tray row and the void beyond", () => {
        expect(resolveTarget(MAP, 5, 400)).toEqual({ kind: "tray", before: 9 });
        expect(resolveTarget(MAP, 200, 400)).toEqual({ kind: "tray", before: null });
        expect(resolveTarget(MAP, 200, 500)).toBeNull();
    });
});

describe("isCarry", () => {
    it("treats short travel as a press and longer travel as a carry", () => {
        expect(isCarry({ x: 0, y: 0 }, { x: CARRY_THRESHOLD, y: 0 })).toBe(false);
        expect(isCarry({ x: 0, y: 0 }, { x: CARRY_THRESHOLD + 1, y: 0 })).toBe(true);
        expect(isCarry({ x: 10, y: 10 }, { x: 14, y: 17 })).toBe(true);
    });
});
