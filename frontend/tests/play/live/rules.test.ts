import { describe, expect, it } from "vitest";

import { FALLBACK_RULES, rulesFrom } from "../../../src/play/live/rules";
import { aDescription, someRules } from "../../fixtures/positions";

describe("rulesFrom", () => {
    it("falls back before the description arrives", () => {
        expect(rulesFrom(null)).toBe(FALLBACK_RULES);
        expect(FALLBACK_RULES.premovesAllowed).toBe(false);
        expect(FALLBACK_RULES.feedback).toBe("submit");
        expect(FALLBACK_RULES.lore).toBe(false);
    });

    it("maps the served parameters onto client rules", () => {
        const rules = rulesFrom(aDescription());
        expect(rules.rackSize).toBe(7);
        expect(rules.exchangeLimit).toBe(3);
        expect(rules.exchangeMinBag).toBe(7);
        expect(rules.passAllowed).toBe(true);
        expect(rules.bingoBonus).toBe(50);
        expect(rules.premovesAllowed).toBe(true);
        expect(rules.feedback).toBe("submit");
        expect(rules.lore).toBe(true);
        expect(rules.alphabet?.map((letter) => letter.symbol)).toEqual(["A", "K"]);
    });

    it("reads a challenge policy from an unvalidated scheme", () => {
        const description = aDescription({ rules: someRules({ validate_on_play: false }) });
        expect(rulesFrom(description).feedback).toBe("challenge");
    });

    it("goes live once the table offers word checks", () => {
        const description = aDescription({ feedback: { word_check: true, lore: true } });
        expect(rulesFrom(description).feedback).toBe("live");
    });
});
