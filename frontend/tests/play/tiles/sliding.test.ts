import { describe, expect, it } from "vitest";

import type { RowPlaces } from "../../../src/play/tiles/sliding";
import { slideDuration, slidesBetween } from "../../../src/play/tiles/sliding";

function places(entries: Record<number, [number, number]>): RowPlaces {
    return new Map(Object.entries(entries).map(([id, [left, top]]) => [Number(id), { left, top }]));
}

describe("slidesBetween", () => {
    it("starts each tile from where it stood", () => {
        const before = places({ 1: [10, 320], 2: [60, 320] });
        const after = places({ 1: [60, 320], 2: [10, 320] });
        expect(slidesBetween(before, after)).toEqual([
            { id: 1, dx: -50, dy: 0 },
            { id: 2, dx: 50, dy: 0 },
        ]);
    });

    it("leaves a tile that kept its place still", () => {
        const before = places({ 1: [10, 320], 2: [60, 320] });
        const after = places({ 1: [10, 320], 2: [110, 320] });
        expect(slidesBetween(before, after)).toEqual([{ id: 2, dx: -50, dy: 0 }]);
    });

    it("ignores a shift too small to see", () => {
        expect(slidesBetween(places({ 1: [10, 320] }), places({ 1: [10.4, 320.2] }))).toEqual([]);
    });

    it("carries a tile across the bands of a wrapped row", () => {
        const before = places({ 3: [10, 372] });
        const after = places({ 3: [110, 324] });
        expect(slidesBetween(before, after)).toEqual([{ id: 3, dx: -100, dy: 48 }]);
    });

    it("lets a tile that has just arrived appear where it is", () => {
        expect(slidesBetween(places({ 1: [10, 320] }), places({ 1: [10, 320], 7: [60, 320] }))).toEqual([]);
    });

    it("forgets a tile the row no longer holds", () => {
        expect(slidesBetween(places({ 1: [10, 320], 2: [60, 320] }), places({ 2: [60, 320] }))).toEqual([]);
    });
});

describe("slideDuration", () => {
    it("reads the token the stylesheet spends", () => {
        expect(slideDuration("150ms")).toBe(150);
        expect(slideDuration(" 150ms ")).toBe(150);
        expect(slideDuration("0.15s")).toBe(150);
    });

    it("stills the row at a zeroed token", () => {
        expect(slideDuration("0s")).toBe(0);
        expect(slideDuration("0ms")).toBe(0);
        expect(slideDuration("none")).toBe(0);
        expect(slideDuration("")).toBe(0);
    });
});
