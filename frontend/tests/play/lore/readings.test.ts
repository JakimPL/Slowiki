import { describe, expect, it } from "vitest";

import {
    askedFormsOf,
    assumedPlayable,
    firstLexeme,
    loreStateOf,
    readingByLexeme,
} from "../../../src/play/lore/readings";
import { aForm, aLore, aReading, someInflection } from "../../fixtures/lore";

describe("loreStateOf", () => {
    it("reads a refused word as absent whatever the sources carry", () => {
        expect(loreStateOf(aLore({ playable: false }))).toBe("absent");
        expect(loreStateOf(aLore({ playable: false, readings: [] }))).toBe("absent");
    });

    it("reads a playable word without readings as unclassified", () => {
        expect(loreStateOf(aLore({ readings: [] }))).toBe("unclassified");
    });

    it("reads a playable word with readings as read", () => {
        expect(loreStateOf(aLore())).toBe("read");
    });
});

describe("askedFormsOf", () => {
    it("keeps the bundles the asked form stands in", () => {
        const nominative = aForm({ tags: someInflection({ cases: ["mianownik"], number: "pojedyncza" }) });
        const vocative = aForm({ tags: someInflection({ cases: ["wołacz"], number: "pojedyncza" }) });
        const genitive = aForm({ text: "PIŁY", tags: someInflection({ cases: ["dopełniacz"] }) });
        const reading = aReading({ forms: [nominative, genitive, vocative] });
        expect(askedFormsOf(reading, "PIŁA")).toEqual([nominative, vocative]);
    });

    it("keeps nothing when the paradigm misses the asked form", () => {
        expect(askedFormsOf(aReading(), "PIŁY")).toEqual([]);
    });
});

describe("readingByLexeme", () => {
    it("finds the reading a lexeme names", () => {
        const drinking = aReading({ lexeme: "czasownik:PIĆ:V", part: "czasownik", base: "pić" });
        const lore = aLore({ readings: [aReading(), drinking] });
        expect(readingByLexeme(lore, "czasownik:PIĆ:V")).toEqual(drinking);
    });

    it("finds nothing for a lexeme the word never carried", () => {
        expect(readingByLexeme(aLore(), "czasownik:PIĆ:V")).toBeNull();
    });
});

describe("firstLexeme", () => {
    it("names the reading a card opens on", () => {
        expect(firstLexeme(aLore())).toBe("rzeczownik:PIŁA:SF");
    });

    it("names nothing when no reading arrived", () => {
        expect(firstLexeme(aLore({ readings: [] }))).toBeNull();
    });
});

describe("assumedPlayable", () => {
    it("takes the chip's refusal as the dictionary's answer", () => {
        expect(assumedPlayable("invalid")).toBe(false);
    });

    it("takes every other chip state as accepted", () => {
        expect(assumedPlayable("valid")).toBe(true);
        expect(assumedPlayable("unknown")).toBe(true);
        expect(assumedPlayable("standing")).toBe(true);
    });
});
