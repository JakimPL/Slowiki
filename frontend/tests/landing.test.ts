import { describe, expect, it } from "vitest";

import { incomingOf, landedRow } from "../src/play/landing";
import { aTile } from "./positions";

const KAY = aTile({ identifier: 7, letter: "K" });
const OH = aTile({ identifier: 8, letter: "O" });
const TEE = aTile({ identifier: 9, letter: "T" });
const ROW = [KAY, OH, TEE];

describe("incomingOf", () => {
    it("claims the region the carry currently points at", () => {
        expect(incomingOf({ kind: "rack", before: 8 }, 7, "rack")).toEqual({ carried: 7, before: 8 });
        expect(incomingOf({ kind: "tray", before: null }, 7, "tray")).toEqual({ carried: 7, before: null });
    });

    it("leaves the other regions alone", () => {
        expect(incomingOf({ kind: "rack", before: 8 }, 7, "tray")).toBeNull();
        expect(incomingOf({ kind: "cell", cell: 112 }, 7, "rack")).toBeNull();
        expect(incomingOf(null, 7, "rack")).toBeNull();
    });
});

describe("landedRow", () => {
    it("keeps the row whole while nothing arrives", () => {
        expect(landedRow(ROW, null)).toEqual({ tiles: ROW, shadowAt: null });
    });

    it("moves the carried tile out of the row and marks where it lands", () => {
        expect(landedRow(ROW, { carried: 7, before: 9 })).toEqual({ tiles: [OH, TEE], shadowAt: 1 });
        expect(landedRow(ROW, { carried: 9, before: 7 })).toEqual({ tiles: [KAY, OH], shadowAt: 0 });
    });

    it("lands at the end of the row without a follower", () => {
        expect(landedRow(ROW, { carried: 7, before: null })).toEqual({ tiles: [OH, TEE], shadowAt: 2 });
    });

    it("makes room for a tile arriving from elsewhere", () => {
        expect(landedRow([OH, TEE], { carried: 7, before: 8 })).toEqual({ tiles: [OH, TEE], shadowAt: 0 });
        expect(landedRow([], { carried: 7, before: null })).toEqual({ tiles: [], shadowAt: 0 });
    });
});
