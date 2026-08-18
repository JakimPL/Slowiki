import { describe, expect, it } from "vitest";

import type { AskedWord } from "../../../src/play/words/asked";
import type { WordChip } from "../../../src/play/words/chips";
import {
    askedWord,
    chose,
    deepened,
    opened,
    PANEL_CLOSED,
    panelStanding,
    retreated,
} from "../../../src/play/words/panel";

const CHIP: WordChip = { text: "PIŁA", points: 7, status: "valid" };
const ACROSS: AskedWord = { text: "PIŁA", points: null, status: "standing" };
const DOWN: AskedWord = { text: "KOT", points: null, status: "standing" };
const LEXEME = "rzeczownik:PIŁA:SF";

describe("opened", () => {
    it("stands at the card with the first word it opened for", () => {
        const panel = opened([CHIP]);
        expect(askedWord(panel)).toBe(CHIP);
        expect(panel.lexeme).toBeNull();
        expect(panelStanding(panel)).toBe(true);
    });

    it("holds the words as a snapshot, so a later draft leaves the panel alone", () => {
        const panel = opened([CHIP]);
        const other: WordChip = { text: "OSA", points: 3, status: "unknown" };
        expect(askedWord(opened([other]))).toBe(other);
        expect(askedWord(panel)).toBe(CHIP);
    });

    it("stays closed when a square carries no word", () => {
        expect(opened([])).toBe(PANEL_CLOSED);
    });
});

describe("chose", () => {
    it("moves to another word at the same square, back at the card", () => {
        const panel = chose(deepened(opened([ACROSS, DOWN]), LEXEME), 1);
        expect(askedWord(panel)).toBe(DOWN);
        expect(panel.lexeme).toBeNull();
    });

    it("rests on a word the panel does not hold", () => {
        const panel = opened([ACROSS]);
        expect(chose(panel, 1)).toBe(panel);
    });
});

describe("deepened", () => {
    it("carries the chosen word into the chosen reading", () => {
        const panel = deepened(opened([CHIP]), LEXEME);
        expect(askedWord(panel)).toBe(CHIP);
        expect(panel.lexeme).toBe(LEXEME);
    });

    it("leaves a closed panel closed", () => {
        expect(deepened(PANEL_CLOSED, LEXEME)).toBe(PANEL_CLOSED);
    });
});

describe("retreated", () => {
    it("steps the sheet back to the card, the card to closed", () => {
        const sheet = deepened(opened([CHIP]), LEXEME);
        const card = retreated(sheet);
        expect(card).toStrictEqual({ words: [CHIP], chosen: 0, lexeme: null });
        expect(retreated(card)).toStrictEqual(PANEL_CLOSED);
    });

    it("keeps the chosen word while stepping back", () => {
        const sheet = deepened(chose(opened([ACROSS, DOWN]), 1), LEXEME);
        expect(askedWord(retreated(sheet))).toBe(DOWN);
    });

    it("rests once closed", () => {
        expect(retreated(PANEL_CLOSED)).toStrictEqual(PANEL_CLOSED);
    });
});

describe("panelStanding", () => {
    it("holds while any depth stands", () => {
        expect(panelStanding(PANEL_CLOSED)).toBe(false);
        expect(panelStanding(opened([CHIP]))).toBe(true);
        expect(panelStanding(deepened(opened([CHIP]), LEXEME))).toBe(true);
    });
});

describe("askedWord", () => {
    it("answers nothing while the panel is closed", () => {
        expect(askedWord(PANEL_CLOSED)).toBeNull();
    });
});
