import { describe, expect, it } from "vitest";

import type { Desk } from "../src/play/desk";
import { affected, EMPTY_DESK, reconciledDesk } from "../src/play/desk";
import { aBoard, aTile } from "./positions";

const KAY = aTile({ identifier: 7, letter: "K" });
const OH = aTile({ identifier: 8, letter: "O" });

describe("desk", () => {
    it("toggles the lift", () => {
        const lifted = affected(EMPTY_DESK, { kind: "lift", tile: KAY });
        expect(lifted.lift?.tile).toEqual(KAY);
        const switched = affected(lifted, { kind: "lift", tile: OH });
        expect(switched.lift?.tile).toEqual(OH);
        expect(affected(switched, { kind: "lift", tile: OH }).lift).toBeNull();
    });

    it("lays the lifted tile and settles the hand", () => {
        const lifted = affected(EMPTY_DESK, { kind: "lift", tile: KAY });
        const laid = affected(lifted, { kind: "lay", cell: 112, letter: null });
        expect(laid.draft).toEqual([{ cell: 112, tile: KAY, letter: null }]);
        expect(laid.lift).toBeNull();
    });

    it("ignores laying with an empty hand or onto a drafted cell", () => {
        expect(affected(EMPTY_DESK, { kind: "lay", cell: 112, letter: null })).toBe(EMPTY_DESK);
        const laid = affected(affected(EMPTY_DESK, { kind: "lift", tile: KAY }), {
            kind: "lay",
            cell: 112,
            letter: null,
        });
        const blocked = affected(affected(laid, { kind: "lift", tile: OH }), {
            kind: "lay",
            cell: 112,
            letter: null,
        });
        expect(blocked).toEqual(affected(laid, { kind: "lift", tile: OH }));
    });

    it("takes back, recalls, and clears the lift", () => {
        const lifted = affected(EMPTY_DESK, { kind: "lift", tile: KAY });
        const laid = affected(lifted, { kind: "lay", cell: 112, letter: null });
        expect(affected(laid, { kind: "take-back", cell: 112 }).draft).toEqual([]);
        expect(affected(laid, { kind: "recall" })).toEqual(EMPTY_DESK);
        expect(affected(lifted, { kind: "clear-lift" }).lift).toBeNull();
    });

    it("reconciles against the served rack and board", () => {
        const laid = affected(affected(EMPTY_DESK, { kind: "lift", tile: KAY }), {
            kind: "lay",
            cell: 112,
            letter: null,
        });
        const desk: Desk = { ...laid, lift: { tile: OH } };
        expect(reconciledDesk(desk, [KAY, OH], aBoard())).toBe(desk);
        expect(reconciledDesk(desk, [OH], aBoard()).draft).toEqual([]);
        expect(reconciledDesk(desk, [KAY], aBoard()).lift).toBeNull();
    });
});
