import { describe, expect, it } from "vitest";

import type { GraspSession } from "../../../src/table/input/dragging";
import {
    aimedOverBoard,
    aimOf,
    carriedTo,
    CARRY_LIFT,
    CARRY_THRESHOLD,
    crowded,
    isCarry,
} from "../../../src/table/input/dragging";
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

describe("aimOf", () => {
    it("aims a mouse carry at the pointer itself", () => {
        expect(aimOf(aSession(false), { x: 50, y: 340 })).toEqual({ x: 50, y: 340 });
    });

    it("aims a touch carry at the tile ghosted above the finger", () => {
        expect(aimOf(aSession(true), { x: 50, y: 340 })).toEqual({ x: 50, y: 340 - CARRY_LIFT });
    });
});

describe("carriedTo", () => {
    const finger = { x: 20, y: 345 + CARRY_LIFT };

    it("lands a touch carry in the row the ghosted tile covers", () => {
        expect(carriedTo(aSession(true), finger).target).toEqual({ kind: "rack", before: 1 });
    });

    it("carries the ghost to the finger while the tile lands above it", () => {
        expect(carriedTo(aSession(true), finger).point).toEqual(finger);
    });

    it("lands a mouse carry under the cursor", () => {
        expect(carriedTo(aSession(false), finger).target).toBeNull();
        expect(carriedTo(aSession(false), { x: 20, y: 345 }).target).toEqual({ kind: "rack", before: 1 });
    });
});

describe("aimedOverBoard", () => {
    it("reads the board from where the player aims rather than where the finger rests", () => {
        expect(aimedOverBoard(aSession(true), { x: 150, y: 290 + CARRY_LIFT })).toBe(true);
        expect(aimedOverBoard(aSession(false), { x: 150, y: 290 + CARRY_LIFT })).toBe(false);
    });
});
