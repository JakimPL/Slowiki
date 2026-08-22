import { describe, expect, it } from "vitest";

import {
    arrangedTiles,
    movedBefore,
    rackOrder,
    reconciledArrangement,
    shuffledArrangement,
} from "../../../src/play/tiles/arrangement";
import { insertedBefore, withoutId } from "../../../src/play/tiles/row";
import { aTile } from "../../fixtures/positions";

describe("row", () => {
    it("inserts before a present id and appends otherwise", () => {
        expect(insertedBefore([1, 2, 3], 3, 1)).toEqual([3, 1, 2]);
        expect(insertedBefore([1, 2, 3], 4, null)).toEqual([1, 2, 3, 4]);
        expect(insertedBefore([1, 2, 3], 4, 9)).toEqual([1, 2, 3, 4]);
        expect(withoutId([1, 2, 3], 2)).toEqual([1, 3]);
    });
});

describe("arrangement", () => {
    const RACK = [aTile({ identifier: 1 }), aTile({ identifier: 2 }), aTile({ identifier: 3 })];

    it("keeps a matching arrangement and rebuilds a stale one", () => {
        const kept = reconciledArrangement([3, 1, 2], RACK);
        expect(kept).toEqual([3, 1, 2]);
        expect(reconciledArrangement([3, 1], RACK)).toEqual([1, 2, 3]);
        expect(reconciledArrangement([3, 1, 2], null)).toEqual([]);
    });

    it("moves ids only when they are present", () => {
        expect(movedBefore([1, 2, 3], 3, 1)).toEqual([3, 1, 2]);
        expect(movedBefore([1, 2, 3], 9, 1)).toEqual([1, 2, 3]);
    });

    it("shuffles only the visible ids and keeps the rest anchored", () => {
        const shuffled = shuffledArrangement([1, 2, 3, 4], new Set([1, 3, 4]), () => 0);
        expect(shuffled.filter((id) => id === 2)).toEqual([2]);
        expect(shuffled[1]).toBe(2);
        expect([...shuffled].sort((left, right) => left - right)).toEqual([1, 2, 3, 4]);
    });

    it("orders tiles by the arrangement", () => {
        const tiles = arrangedTiles([3, 1, 2], RACK);
        expect(tiles.map((tile) => tile.identifier)).toEqual([3, 1, 2]);
    });

    it("builds the remembered order as rack row, tray, then drafted", () => {
        expect(rackOrder([5, 4, 3, 2, 1], [4, 2], new Set([3]))).toEqual([5, 1, 4, 2, 3]);
        expect(rackOrder([1, 2, 3], [], new Set())).toEqual([1, 2, 3]);
    });
});
