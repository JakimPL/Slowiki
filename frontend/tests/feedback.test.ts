import { describe, expect, it } from "vitest";

import { invalidTextsOf, policyOf, wordStatusFor } from "../src/play/feedback";
import { NO_JUDGEMENTS } from "../src/play/verdicts";

describe("feedback", () => {
    it("derives the policy from the validation flag and the word check", () => {
        expect(policyOf(true, false)).toBe("submit");
        expect(policyOf(false, false)).toBe("challenge");
        expect(policyOf(true, true)).toBe("live");
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
        expect(wordStatusFor("submit", "KOTZ", refused, NO_JUDGEMENTS)).toBe("invalid");
        expect(wordStatusFor("submit", "DOM", refused, NO_JUDGEMENTS)).toBe("unknown");
        expect(wordStatusFor("challenge", "DOM", new Set(), NO_JUDGEMENTS)).toBe("standing");
    });

    it("shows the dictionary's word verdicts while the policy is live", () => {
        const judged = new Map([
            ["DOM", true],
            ["KOTZ", false],
        ]);
        expect(wordStatusFor("live", "DOM", new Set(), judged)).toBe("valid");
        expect(wordStatusFor("live", "KOTZ", new Set(), judged)).toBe("invalid");
        expect(wordStatusFor("live", "OSA", new Set(), judged)).toBe("unknown");
    });
});
