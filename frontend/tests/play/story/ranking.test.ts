import { describe, expect, it } from "vitest";

import { rankingOf } from "../../../src/play/story/ranking";
import { aView } from "../../fixtures/positions";

describe("rankingOf", () => {
    it("ranks the players by points, highest first", () => {
        const view = aView({ players: [0, 1, 2], scores: { 0: 30, 1: 42, 2: 12 } });
        expect(rankingOf(view)).toEqual([
            { seat: 1, points: 42, place: 1 },
            { seat: 0, points: 30, place: 2 },
            { seat: 2, points: 12, place: 3 },
        ]);
    });

    it("gives tied players the same place and skips the one they share", () => {
        const view = aView({ players: [0, 1, 2], scores: { 0: 42, 1: 42, 2: 12 } });
        expect(rankingOf(view).map((placing) => placing.place)).toEqual([1, 1, 3]);
    });

    it("orders a tie by seat and reads a missing score as nothing", () => {
        const view = aView({ players: [1, 0], scores: { 1: 7 } });
        expect(rankingOf(view)).toEqual([
            { seat: 1, points: 7, place: 1 },
            { seat: 0, points: 0, place: 2 },
        ]);
    });
});
