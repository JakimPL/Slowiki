import { describe, expect, it } from "vitest";

import { crowded, isCarry } from "../../../src/table/input/dragging";

describe("isCarry", () => {
    it("keeps a press in place a tap", () => {
        expect(isCarry({ x: 100, y: 100 }, { x: 104, y: 100 })).toBe(false);
    });

    it("reads travel past the threshold as a carry", () => {
        expect(isCarry({ x: 100, y: 100 }, { x: 110, y: 100 })).toBe(true);
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
