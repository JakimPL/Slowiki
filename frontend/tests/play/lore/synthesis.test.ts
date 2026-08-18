import { describe, expect, it } from "vitest";

import type { LoreReading, WordLore } from "../../../src/api/lore";
import { paradigmOf } from "../../../src/play/lore/paradigm";
import { askedFormsOf } from "../../../src/play/lore/readings";
import { synthesisFor } from "../../../src/play/lore/synthesis";

const WORDS: readonly string[] = ["KOSA", "ŁÓDŹ", "GRA", "PISK", "WĄŻ", "SÓL", "TRAWA", "MIŁOŚĆ", "ZUPA"];

function onlyReading(lore: WordLore): LoreReading {
    const reading = lore.readings[0];
    if (reading === undefined) {
        throw new Error(`the synthesis of ${lore.word} carries no reading`);
    }
    return reading;
}

describe("synthesisFor", () => {
    it("fabricates a paradigm around the one form the dictionary answered for", () => {
        const lore = synthesisFor("KOSA");
        expect(lore.word).toBe("KOSA");
        expect(lore.playable).toBe(true);
        const forms = onlyReading(lore).forms;
        expect(forms.filter((form) => form.playable).map((form) => form.text)).toEqual(["KOSA"]);
        expect(forms.length).toBeGreaterThan(1);
    });

    it("stands the asked word in the paradigm it fabricates", () => {
        for (const word of WORDS) {
            expect(askedFormsOf(onlyReading(synthesisFor(word)), word), word).toHaveLength(1);
        }
    });

    it("names a base form that stands in the same paradigm", () => {
        for (const word of WORDS) {
            const reading = onlyReading(synthesisFor(word));
            expect(
                reading.forms.map((form) => form.text),
                word,
            ).toContain(reading.base);
        }
    });

    it("keeps every fabricated text in canonical uppercase", () => {
        for (const word of WORDS) {
            for (const form of onlyReading(synthesisFor(word)).forms) {
                expect(form.text).toBe(form.text.toUpperCase());
            }
        }
    });

    it("gives one word the same shape every time", () => {
        expect(synthesisFor("TRAWA")).toEqual(synthesisFor("TRAWA"));
    });

    it("picks one of three shapes by the letters of the word", () => {
        const parts = WORDS.map((word) => onlyReading(synthesisFor(word)).part);
        expect(new Set(parts)).toEqual(new Set(["rzeczownik", "przymiotnik", "czasownik"]));
    });

    it("lays out every fabricated paradigm without leftovers", () => {
        for (const word of WORDS) {
            const reading = onlyReading(synthesisFor(word));
            const paradigm = paradigmOf(reading);
            expect(paradigm.rest, word).toEqual([]);
            expect(paradigm.grids.length + paradigm.lists.length, word).toBeGreaterThan(0);
        }
    });
});
