import { describe, expect, it } from "vitest";

import { invalidTextsOf, policyOf, wordStatusFor } from "../src/play/feedback";

describe("feedback", () => {
    it("derives the policy from the validation flag", () => {
        expect(policyOf(true)).toBe("submit");
        expect(policyOf(false)).toBe("challenge");
    });

    it("reads refused word texts from an invalid-word notice", () => {
        const texts = invalidTextsOf("invalid_word", "invalid words: KOTZ, ABC");
        expect(texts).toEqual(new Set(["KOTZ", "ABC"]));
        expect(invalidTextsOf("stale_position", "invalid words: KOTZ")).toEqual(new Set());
        expect(invalidTextsOf("invalid_word", "something else")).toEqual(new Set());
        expect(invalidTextsOf(null, null)).toEqual(new Set());
    });

    it("marks refused words and lets the policy shade the rest", () => {
        const refused = new Set(["KOTZ"]);
        expect(wordStatusFor("submit", "KOTZ", refused)).toBe("invalid");
        expect(wordStatusFor("submit", "DOM", refused)).toBe("unknown");
        expect(wordStatusFor("challenge", "DOM", new Set())).toBe("standing");
    });
});
