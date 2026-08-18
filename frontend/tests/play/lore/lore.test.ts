import { describe, expect, it } from "vitest";

import { loreFor, SAMPLE_SOURCE } from "../../../src/play/lore/lore";
import { paradigmOf } from "../../../src/play/lore/paradigm";
import { askedFormsOf, loreStateOf } from "../../../src/play/lore/readings";
import { SPECIMEN_WORDS } from "../../../src/play/lore/specimens";

describe("loreFor", () => {
    it("answers a refused word as absent whatever the sources hold", () => {
        expect(loreFor("PIŁA", false)).toEqual({ word: "PIŁA", playable: false, readings: [] });
        expect(loreStateOf(loreFor("ZQX", false))).toBe("absent");
    });

    it("answers a specimen word from the authored lore", () => {
        const lore = loreFor("PIŁA", true);
        expect(lore.readings.map((reading) => reading.part)).toEqual(["rzeczownik", "czasownik"]);
        expect(loreStateOf(lore)).toBe("read");
    });

    it("answers a word the sources leave open as unclassified", () => {
        expect(loreStateOf(loreFor("ĆWIR", true))).toBe("unclassified");
    });

    it("answers an unknown word from the synthetic fallback", () => {
        const lore = loreFor("KOSA", true);
        expect(lore.readings).toHaveLength(1);
        expect(loreStateOf(lore)).toBe("read");
    });

    it("badges everything it answers as sample data", () => {
        expect(SAMPLE_SOURCE).toBe(true);
    });
});

describe("the authored specimens", () => {
    it("answers every specimen under its own word", () => {
        for (const word of SPECIMEN_WORDS) {
            expect(loreFor(word, true).word).toBe(word);
        }
    });

    it("stands the asked word in every reading it carries", () => {
        for (const word of SPECIMEN_WORDS) {
            for (const reading of loreFor(word, true).readings) {
                expect(askedFormsOf(reading, word).length, `${word} · ${reading.lexeme}`).toBeGreaterThan(0);
            }
        }
    });

    it("names a base form that stands in the same paradigm", () => {
        for (const word of SPECIMEN_WORDS) {
            for (const reading of loreFor(word, true).readings) {
                expect(
                    reading.forms.map((form) => form.text),
                    `${word} · ${reading.lexeme}`,
                ).toContain(reading.base);
            }
        }
    });

    it("keeps every authored text in canonical uppercase", () => {
        for (const word of SPECIMEN_WORDS) {
            expect(word).toBe(word.toUpperCase());
            for (const reading of loreFor(word, true).readings) {
                expect(reading.base).toBe(reading.base.toUpperCase());
                for (const form of reading.forms) {
                    expect(form.text).toBe(form.text.toUpperCase());
                }
            }
        }
    });

    it("lays out every authored paradigm without leftovers", () => {
        for (const word of SPECIMEN_WORDS) {
            for (const reading of loreFor(word, true).readings) {
                const paradigm = paradigmOf(reading);
                const label = `${word} · ${reading.lexeme}`;
                expect(paradigm.rest, label).toEqual([]);
                expect(paradigm.grids.length + paradigm.lists.length, label).toBeGreaterThan(0);
            }
        }
    });

    it("names every reading by a lexeme of its own", () => {
        const lexemes = SPECIMEN_WORDS.flatMap((word) => loreFor(word, true).readings.map((reading) => reading.lexeme));
        expect(new Set(lexemes).size).toBe(lexemes.length);
    });
});
