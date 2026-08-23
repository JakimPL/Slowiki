import { describe, expect, it } from "vitest";

import type { GraspSession } from "../../../src/table/input/dragging";
import { carriedTo, CARRY_THRESHOLD, crowded, isCarry } from "../../../src/table/input/dragging";
import type { TargetMap } from "../../../src/table/input/targets";
import { aTile } from "../../fixtures/positions";

const TARGETS: TargetMap = {
    size: 15,
    board: { left: 0, top: 0, width: 300, height: 300 },
    viewport: { left: 0, top: 0, width: 300, height: 300 },
    rows: [
        {
            region: "rack",
            rect: { left: 0, top: 320, width: 300, height: 50 },
            slots: [{ id: 1, rect: { left: 10, top: 324, width: 40, height: 42 } }],
        },
    ],
};

function aSession(touch: boolean): GraspSession {
    return {
        grasp: { spot: { kind: "rack" }, tile: aTile() },
        start: { x: 0, y: 0 },
        touch,
        targets: TARGETS,
        carrying: true,
    };
}

describe("isCarry", () => {
    it("keeps a press in place a tap", () => {
        expect(isCarry({ x: 100, y: 100 }, { x: 104, y: 100 })).toBe(false);
        expect(isCarry({ x: 0, y: 0 }, { x: CARRY_THRESHOLD, y: 0 })).toBe(false);
    });

    it("reads travel past the threshold as a carry", () => {
        expect(isCarry({ x: 100, y: 100 }, { x: 110, y: 100 })).toBe(true);
        expect(isCarry({ x: 0, y: 0 }, { x: CARRY_THRESHOLD + 1, y: 0 })).toBe(true);
        expect(isCarry({ x: 10, y: 10 }, { x: 14, y: 17 })).toBe(true);
    });

    it("ends a building press-and-hold at the distance that starts a carry", () => {
        expect(isCarry({ x: 40, y: 40 }, { x: 43, y: 43 })).toBe(false);
        expect(isCarry({ x: 40, y: 40 }, { x: 46, y: 46 })).toBe(true);
    });
});

describe("crowded", () => {
    it("leaves one pointer to the tile it grasped", () => {
        expect(crowded(new Set())).toBe(false);
        expect(crowded(new Set([1]))).toBe(false);
    });

    it("declares the gesture the moment a second pointer arrives", () => {
        expect(crowded(new Set([1, 2]))).toBe(true);
        expect(crowded(new Set([1, 2, 3]))).toBe(true);
    });
});

describe("carriedTo", () => {
    const pointer = { x: 20, y: 345 };

    it("lands a carry in the row the pointer rests on, finger and cursor alike", () => {
        expect(carriedTo(aSession(true), pointer).target).toEqual({ kind: "rack", before: 1 });
        expect(carriedTo(aSession(false), pointer).target).toEqual({ kind: "rack", before: 1 });
    });

    it("lands a carry in the square the pointer rests on", () => {
        expect(carriedTo(aSession(true), { x: 150, y: 290 }).target).toEqual({ kind: "cell", cell: 217 });
    });

    it("carries the ghost to the pointer that drags it", () => {
        expect(carriedTo(aSession(true), pointer).point).toEqual(pointer);
    });
});
