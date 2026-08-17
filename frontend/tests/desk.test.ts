import { describe, expect, it } from "vitest";

import type { Desk, DeskEffect } from "../src/play/desk";
import { affected, EMPTY_DESK, reconciledDesk } from "../src/play/desk";
import { aBoard, aTile } from "./positions";

const KAY = aTile({ identifier: 7, letter: "K" });
const OH = aTile({ identifier: 8, letter: "O" });
const TEE = aTile({ identifier: 9, letter: "T" });

function performed(...effects: readonly DeskEffect[]): Desk {
    return effects.reduce(affected, EMPTY_DESK);
}

describe("desk", () => {
    it("toggles the lift and remembers its source", () => {
        const lifted = performed({ kind: "lift", tile: KAY, from: { kind: "rack" } });
        expect(lifted.lift).toEqual({ tile: KAY, from: { kind: "rack" } });
        const switched = affected(lifted, { kind: "lift", tile: OH, from: { kind: "tray" } });
        expect(switched.lift).toEqual({ tile: OH, from: { kind: "tray" } });
        expect(affected(switched, { kind: "lift", tile: OH, from: { kind: "tray" } }).lift).toBeNull();
    });

    it("lays a tile, settling the hand and leaving the tray", () => {
        const desk = performed(
            { kind: "park", id: KAY.identifier, before: null },
            { kind: "lift", tile: KAY, from: { kind: "tray" } },
            { kind: "lay", cell: 112, tile: KAY, letter: null },
        );
        expect(desk.draft).toEqual([{ cell: 112, tile: KAY, letter: null }]);
        expect(desk.lift).toBeNull();
        expect(desk.tray).toEqual([]);
    });

    it("keeps a drafted cell occupied", () => {
        const desk = performed(
            { kind: "lay", cell: 112, tile: KAY, letter: null },
            { kind: "lay", cell: 112, tile: OH, letter: null },
        );
        expect(desk.draft).toEqual([{ cell: 112, tile: KAY, letter: null }]);
    });

    it("relays a pending tile and keeps its blank letter", () => {
        const desk = performed(
            { kind: "lay", cell: 112, tile: KAY, letter: "Ż" },
            { kind: "relay", from: 112, to: 113 },
        );
        expect(desk.draft).toEqual([{ cell: 113, tile: KAY, letter: "Ż" }]);
        expect(affected(desk, { kind: "relay", from: 113, to: 113 }).draft).toEqual(desk.draft);
    });

    it("sets the tile down wherever the lift ends", () => {
        const lifted = performed(
            { kind: "lay", cell: 112, tile: KAY, letter: null },
            { kind: "lift", tile: KAY, from: { kind: "cell", cell: 112 } },
        );
        expect(affected(lifted, { kind: "relay", from: 112, to: 113 }).lift).toBeNull();
        expect(affected(lifted, { kind: "take-back", cell: 112 }).lift).toBeNull();
        const held = performed(
            { kind: "arrange", arrangement: [7, 8] },
            { kind: "lift", tile: KAY, from: { kind: "rack" } },
        );
        expect(affected(held, { kind: "reorder", id: 7, before: 8 }).lift).toBeNull();
        expect(affected(held, { kind: "take-back", cell: 112 }).lift).toEqual(held.lift);
    });

    it("parks, retrieves, and reorders by identifier", () => {
        const parkedDesk = performed(
            { kind: "arrange", arrangement: [7, 8, 9] },
            { kind: "park", id: 8, before: null },
            { kind: "park", id: 7, before: 8 },
        );
        expect(parkedDesk.tray).toEqual([7, 8]);
        const retrieved = affected(parkedDesk, { kind: "retrieve", id: 8, before: 7 });
        expect(retrieved.tray).toEqual([7]);
        expect(retrieved.arrangement).toEqual([8, 7, 9]);
        const reordered = affected(retrieved, { kind: "reorder", id: 9, before: 8 });
        expect(reordered.arrangement).toEqual([9, 8, 7]);
    });

    it("takes back, recalls, and clears the lift", () => {
        const laid = performed({ kind: "lay", cell: 112, tile: KAY, letter: null });
        expect(affected(laid, { kind: "take-back", cell: 112 }).draft).toEqual([]);
        const messy = affected(affected(laid, { kind: "park", id: OH.identifier, before: null }), {
            kind: "lift",
            tile: TEE,
            from: { kind: "rack" },
        });
        const recalled = affected(messy, { kind: "recall" });
        expect(recalled.draft).toEqual([]);
        expect(recalled.lift).toBeNull();
        expect(recalled.tray).toEqual([OH.identifier]);
        expect(affected(messy, { kind: "clear-lift" }).lift).toBeNull();
    });

    it("reconciles the draft, tray, arrangement, and lift against the view", () => {
        const desk = performed(
            { kind: "arrange", arrangement: [9, 7, 8] },
            { kind: "park", id: 8, before: null },
            { kind: "lay", cell: 112, tile: KAY, letter: null },
            { kind: "lift", tile: TEE, from: { kind: "rack" } },
        );
        const free = new Set<number>();
        expect(reconciledDesk(desk, [KAY, OH, TEE], aBoard(), free)).toBe(desk);
        const shrunk = reconciledDesk(desk, [KAY, TEE], aBoard(), free);
        expect(shrunk.tray).toEqual([]);
        expect(shrunk.arrangement).toEqual([7, 9]);
        const emptied = reconciledDesk(desk, null, aBoard(), free);
        expect(emptied).toEqual(EMPTY_DESK);
    });

    it("releases drafted and lifted tiles once a premove commits them", () => {
        const desk = performed(
            { kind: "lay", cell: 112, tile: KAY, letter: null },
            { kind: "lift", tile: TEE, from: { kind: "rack" } },
        );
        const committed = reconciledDesk(desk, [KAY, OH, TEE], aBoard(), new Set([KAY.identifier, TEE.identifier]));
        expect(committed.draft).toEqual([]);
        expect(committed.lift).toBeNull();
    });
});
