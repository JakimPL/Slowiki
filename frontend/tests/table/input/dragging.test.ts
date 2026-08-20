import { describe, expect, it } from "vitest";

import { CARRY_THRESHOLD, crowded, isCarry } from "../../../src/table/input/dragging";

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
