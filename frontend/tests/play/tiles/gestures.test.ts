import { describe, expect, it } from "vitest";

import { affected, EMPTY_DESK } from "../../../src/play/tiles/desk";
import { blankLanding, dropEffects, tapEffects } from "../../../src/play/tiles/gestures";
import type { Lift } from "../../../src/play/tiles/selection";
import { aTile } from "../../fixtures/positions";

const KAY = aTile({ identifier: 7, letter: "K" });
const OH = aTile({ identifier: 8, letter: "O" });
const BLANK = aTile({ identifier: 9, letter: "", value: 0, blank: true });

const CELL = 112;
const ELSEWHERE = 113;

const fromRack: Lift = { tile: KAY, from: { kind: "rack" } };
const fromTray: Lift = { tile: KAY, from: { kind: "tray" } };
const fromCell: Lift = { tile: KAY, from: { kind: "cell", cell: CELL } };

describe("tapEffects", () => {
    it("lifts the tapped tile wherever it rests", () => {
        expect(tapEffects(null, { kind: "rack" }, KAY)).toEqual([{ kind: "lift", tile: KAY, from: { kind: "rack" } }]);
        expect(tapEffects(null, { kind: "tray" }, KAY)).toEqual([{ kind: "lift", tile: KAY, from: { kind: "tray" } }]);
        expect(tapEffects(null, { kind: "cell", cell: CELL }, KAY)).toEqual([
            { kind: "lift", tile: KAY, from: { kind: "cell", cell: CELL } },
        ]);
    });

    it("puts a lifted tile down again on a second tap", () => {
        const lifted = affected(EMPTY_DESK, { kind: "lift", tile: KAY, from: { kind: "cell", cell: CELL } });
        const effects = tapEffects(lifted.lift, { kind: "cell", cell: CELL }, KAY);
        expect(effects.reduce(affected, lifted).lift).toBeNull();
    });

    it("switches the lift within one region", () => {
        expect(tapEffects(fromRack, { kind: "rack" }, OH)).toEqual([
            { kind: "lift", tile: OH, from: { kind: "rack" } },
        ]);
    });

    it("lands a lifted tile beside the tile tapped in another region", () => {
        expect(tapEffects(fromTray, { kind: "rack" }, OH)).toEqual([{ kind: "retrieve", id: 7, before: 8 }]);
        expect(tapEffects(fromRack, { kind: "tray" }, OH)).toEqual([{ kind: "park", id: 7, before: 8 }]);
    });

    it("brings a lifted board tile back to the tapped row position", () => {
        expect(tapEffects(fromCell, { kind: "rack" }, OH)).toEqual([
            { kind: "take-back", cell: CELL },
            { kind: "reorder", id: 7, before: 8 },
        ]);
        expect(tapEffects(fromCell, { kind: "tray" }, OH)).toEqual([
            { kind: "take-back", cell: CELL },
            { kind: "park", id: 7, before: 8 },
        ]);
    });
});

describe("dropEffects", () => {
    it("lays a rack tile on an empty cell", () => {
        expect(dropEffects({ kind: "rack" }, KAY, { kind: "cell", cell: CELL }, true)).toEqual([
            { kind: "lay", cell: CELL, tile: KAY, letter: null },
        ]);
    });

    it("lays a blank face down and names the cell awaiting its letter", () => {
        expect(dropEffects({ kind: "rack" }, BLANK, { kind: "cell", cell: CELL }, true)).toEqual([
            { kind: "lay", cell: CELL, tile: BLANK, letter: null },
        ]);
        expect(blankLanding({ kind: "rack" }, BLANK, { kind: "cell", cell: CELL })).toBe(CELL);
        expect(blankLanding({ kind: "rack" }, KAY, { kind: "cell", cell: CELL })).toBeNull();
        expect(blankLanding({ kind: "cell", cell: CELL }, BLANK, { kind: "cell", cell: ELSEWHERE })).toBeNull();
        expect(blankLanding({ kind: "rack" }, BLANK, { kind: "rack", before: null })).toBeNull();
    });

    it("relays a pending tile between cells and rests on its own square", () => {
        expect(dropEffects({ kind: "cell", cell: CELL }, KAY, { kind: "cell", cell: ELSEWHERE }, true)).toEqual([
            { kind: "relay", from: CELL, to: ELSEWHERE },
        ]);
        expect(dropEffects({ kind: "cell", cell: CELL }, KAY, { kind: "cell", cell: CELL }, true)).toEqual([]);
    });

    it("keeps the board out of reach while the seat may not act", () => {
        expect(dropEffects({ kind: "rack" }, KAY, { kind: "cell", cell: CELL }, false)).toEqual([]);
    });

    it("reorders, parks, and retrieves along the rows", () => {
        expect(dropEffects({ kind: "rack" }, KAY, { kind: "rack", before: 8 }, true)).toEqual([
            { kind: "reorder", id: 7, before: 8 },
        ]);
        expect(dropEffects({ kind: "tray" }, KAY, { kind: "rack", before: null }, true)).toEqual([
            { kind: "retrieve", id: 7, before: null },
        ]);
        expect(dropEffects({ kind: "rack" }, KAY, { kind: "tray", before: null }, true)).toEqual([
            { kind: "park", id: 7, before: null },
        ]);
        expect(dropEffects({ kind: "cell", cell: CELL }, KAY, { kind: "rack", before: 8 }, true)).toEqual([
            { kind: "take-back", cell: CELL },
            { kind: "reorder", id: 7, before: 8 },
        ]);
    });

    it("takes a pending tile back when it lands outside every region", () => {
        expect(dropEffects({ kind: "cell", cell: CELL }, KAY, null, true)).toEqual([{ kind: "take-back", cell: CELL }]);
        expect(dropEffects({ kind: "rack" }, KAY, null, true)).toEqual([]);
    });
});
