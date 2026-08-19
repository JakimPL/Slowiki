import { describe, expect, it } from "vitest";

import { askedPlayed, askedStanding } from "../../../src/play/words/asked";

describe("askedPlayed", () => {
    it("keeps the score the table gave the word and reads it as standing", () => {
        expect(askedPlayed({ text: "PIŁA", points: 24 })).toStrictEqual({
            text: "PIŁA",
            points: 24,
            status: "standing",
        });
    });
});

describe("askedStanding", () => {
    it("carries no score, since the bonuses under a standing word are spent", () => {
        expect(askedStanding("KOT")).toStrictEqual({ text: "KOT", points: null, status: "standing" });
    });
});
