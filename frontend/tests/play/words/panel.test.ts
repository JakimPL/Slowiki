import { describe, expect, it } from "vitest";

import type { WordChip } from "../../../src/play/words/chips";
import { deepened, opened, PANEL_CLOSED, panelStanding, retreated } from "../../../src/play/words/panel";

const CHIP: WordChip = { text: "PIŁA", points: 7, status: "valid" };
const LEXEME = "rzeczownik:PIŁA:SF";

describe("opened", () => {
    it("stands at the card with the chip it opened for", () => {
        const panel = opened(CHIP);
        expect(panel.chip).toBe(CHIP);
        expect(panel.lexeme).toBeNull();
        expect(panelStanding(panel)).toBe(true);
    });

    it("holds the chip as a snapshot, so a later draft leaves the panel alone", () => {
        const panel = opened(CHIP);
        const other: WordChip = { text: "OSA", points: 3, status: "unknown" };
        expect(opened(other).chip).toBe(other);
        expect(panel.chip).toBe(CHIP);
    });
});

describe("deepened", () => {
    it("carries the chip into the chosen reading", () => {
        const panel = deepened(opened(CHIP), LEXEME);
        expect(panel.chip).toBe(CHIP);
        expect(panel.lexeme).toBe(LEXEME);
    });

    it("leaves a closed panel closed", () => {
        expect(deepened(PANEL_CLOSED, LEXEME)).toBe(PANEL_CLOSED);
    });
});

describe("retreated", () => {
    it("steps the sheet back to the card, the card to closed", () => {
        const sheet = deepened(opened(CHIP), LEXEME);
        const card = retreated(sheet);
        expect(card).toStrictEqual({ chip: CHIP, lexeme: null });
        expect(retreated(card)).toStrictEqual(PANEL_CLOSED);
    });

    it("rests once closed", () => {
        expect(retreated(PANEL_CLOSED)).toStrictEqual(PANEL_CLOSED);
    });
});

describe("panelStanding", () => {
    it("holds while any depth stands", () => {
        expect(panelStanding(PANEL_CLOSED)).toBe(false);
        expect(panelStanding(opened(CHIP))).toBe(true);
        expect(panelStanding(deepened(opened(CHIP), LEXEME))).toBe(true);
    });
});
