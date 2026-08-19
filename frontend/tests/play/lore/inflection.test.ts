import { describe, expect, it } from "vitest";

import { inflectionTerms } from "../../../src/play/lore/inflection";
import { DEPRECATIVE_TERM, NEGATED_TERM } from "../../../src/play/lore/tagset";
import { someInflection } from "../../fixtures/lore";

describe("inflectionTerms", () => {
    it("reads a noun bundle as case, number and gender", () => {
        const tags = someInflection({ cases: ["mianownik"], numbers: ["pojedyncza"], genders: ["żeński"] });
        expect(inflectionTerms(tags, [])).toEqual(["mianownik", "pojedyncza", "żeński"]);
    });

    it("opens a verb bundle with the form and its mood and tense", () => {
        const tags = someInflection({
            verb_form: "forma przeszła",
            mood: "oznajmujący",
            tense: "przeszły",
            numbers: ["pojedyncza"],
            genders: ["męskoosobowy"],
        });
        expect(inflectionTerms(tags, [])).toEqual([
            "forma przeszła",
            "oznajmujący",
            "przeszły",
            "pojedyncza",
            "męskoosobowy",
        ]);
    });

    it("puts the terms of one dimension in their canonical order", () => {
        const tags = someInflection({ cases: ["biernik", "mianownik"], genders: ["żeński", "męskoosobowy"] });
        expect(inflectionTerms(tags, [])).toEqual(["mianownik", "biernik", "męskoosobowy", "żeński"]);
    });

    it("drops the dimensions a surrounding heading already prints", () => {
        const tags = someInflection({ cases: ["mianownik"], numbers: ["pojedyncza"], genders: ["żeński"] });
        expect(inflectionTerms(tags, ["case", "number"])).toEqual(["żeński"]);
        expect(inflectionTerms(tags, ["case", "number", "gender"])).toEqual([]);
    });

    it("prints the negated and deprecative forms as their own terms", () => {
        const negated = someInflection({ verb_form: "imiesłów bierny", negation: true });
        expect(inflectionTerms(negated, [])).toEqual(["imiesłów bierny", NEGATED_TERM]);
        const affirmative = someInflection({ verb_form: "imiesłów bierny", negation: false });
        expect(inflectionTerms(affirmative, [])).toEqual(["imiesłów bierny"]);
        const deprecative = someInflection({ cases: ["mianownik"], numbers: ["mnoga"], deprecative: true });
        expect(inflectionTerms(deprecative, [])).toEqual(["mianownik", "mnoga", DEPRECATIVE_TERM]);
    });

    it("reads an invariant part as no terms at all", () => {
        expect(inflectionTerms(someInflection(), [])).toEqual([]);
    });
});
