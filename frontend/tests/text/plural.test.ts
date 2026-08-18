import { describe, expect, it } from "vitest";

import { pluralCategory } from "../../src/text/plural";

describe("pluralCategory", () => {
    it("separates a single English thing from every other count", () => {
        expect(pluralCategory("en", 1)).toBe("one");
        expect(pluralCategory("en", 0)).toBe("other");
        expect(pluralCategory("en", 2)).toBe("other");
        expect(pluralCategory("en", 21)).toBe("other");
    });

    it("follows the Polish one, few and many pattern", () => {
        expect(pluralCategory("pl", 1)).toBe("one");
        expect(pluralCategory("pl", 2)).toBe("few");
        expect(pluralCategory("pl", 4)).toBe("few");
        expect(pluralCategory("pl", 22)).toBe("few");
        expect(pluralCategory("pl", 5)).toBe("many");
        expect(pluralCategory("pl", 0)).toBe("many");
        expect(pluralCategory("pl", 12)).toBe("many");
        expect(pluralCategory("pl", 113)).toBe("many");
    });
});
