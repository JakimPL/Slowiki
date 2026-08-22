import { describe, expect, it } from "vitest";

import { wordRefused } from "../../../src/play/words/chips";

describe("wordRefused", () => {
    it("rests the play on a word the dictionary turned down", () => {
        expect(wordRefused([{ text: "KOT", points: 5, status: "invalid" }])).toBe(true);
        expect(
            wordRefused([
                { text: "KOT", points: 5, status: "valid" },
                { text: "OS", points: 2, status: "invalid" },
            ]),
        ).toBe(true);
    });

    it("arms the play while every word stands or waits on an answer", () => {
        expect(wordRefused([])).toBe(false);
        expect(wordRefused([{ text: "KOT", points: 5, status: "valid" }])).toBe(false);
        expect(wordRefused([{ text: "KOT", points: 5, status: "unknown" }])).toBe(false);
        expect(wordRefused([{ text: "KOT", points: 5, status: "standing" }])).toBe(false);
    });
});
