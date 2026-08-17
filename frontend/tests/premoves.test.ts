import { describe, expect, it } from "vitest";

import type { LogEntry } from "../src/play/log";
import { queuedPremoveOf, returnedPremoveOf } from "../src/play/premoves";
import { aTile, aView } from "./positions";

const KAY = aTile({ identifier: 7, letter: "K" });
const BLANK = aTile({ identifier: 8, letter: "", blank: true });

describe("queuedPremoveOf", () => {
    it("mirrors a queued play as board ghosts with blank letters resolved", () => {
        const view = aView({
            racks: { 0: [KAY, BLANK], 1: null },
            premove: {
                player: 0,
                action: {
                    kind: "play",
                    placements: [
                        { tile_id: 7, row: 7, column: 7, letter: null },
                        { tile_id: 8, row: 7, column: 8, letter: "Ż" },
                    ],
                },
            },
            pending_premoves: [0],
        });
        const queued = queuedPremoveOf(view, 0);
        expect(queued?.kind).toBe("play");
        expect(queued?.ghosts).toEqual([
            { cell: 112, tile: KAY },
            { cell: 113, tile: { ...BLANK, letter: "Ż" } },
        ]);
        expect(queued?.committed).toEqual(new Set([7, 8]));
    });

    it("mirrors a queued exchange as committed tiles without ghosts", () => {
        const view = aView({
            racks: { 0: [KAY, BLANK], 1: null },
            premove: { player: 0, action: { kind: "exchange", tile_ids: [8] } },
            pending_premoves: [0],
        });
        const queued = queuedPremoveOf(view, 0);
        expect(queued?.kind).toBe("exchange");
        expect(queued?.ghosts).toEqual([]);
        expect(queued?.committed).toEqual(new Set([8]));
    });

    it("stays empty without a queued premove or a seat", () => {
        expect(queuedPremoveOf(aView(), 0)).toBeNull();
        const queuedView = aView({ premove: { player: 0, action: { kind: "pass" } } });
        expect(queuedPremoveOf(queuedView, 0)).toBeNull();
        expect(queuedPremoveOf(aView(), null)).toBeNull();
    });
});

describe("returnedPremoveOf", () => {
    const returned: LogEntry = { seq: 4, actor: 0, kind: "premove-returned", words: [], points: null, reason: null };
    const play: LogEntry = { seq: 5, actor: 1, kind: "play", words: [], points: 3, reason: null };

    it("finds my latest returned premove behind newer entries", () => {
        expect(returnedPremoveOf([returned, play], 0)).toBe(returned);
    });

    it("ignores other seats' returns and empty logs", () => {
        expect(returnedPremoveOf([returned, play], 1)).toBeNull();
        expect(returnedPremoveOf([], 0)).toBeNull();
        expect(returnedPremoveOf([play], null)).toBeNull();
    });
});
