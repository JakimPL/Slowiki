import { describe, expect, it } from "vitest";

import type { Case } from "../src/api/lore";
import type { Dimension } from "../src/play/tagset";
import {
    ASPECT_ORDER,
    CASE_ORDER,
    compareInflections,
    DEGREE_ORDER,
    DEPRECATIVE_TERM,
    DIMENSION_ORDER,
    GENDER_ORDER,
    inOrder,
    MOOD_ORDER,
    NUMBER_ORDER,
    NUMERAL_TYPE_ORDER,
    PART_ORDER,
    PERSON_ORDER,
    PRONOUN_TYPE_ORDER,
    TENSE_ORDER,
    termsOn,
    VERB_FORM_ORDER,
} from "../src/play/tagset";
import { someInflection } from "./lore";

const EVERY_DIMENSION: Record<Dimension, true> = {
    verbForm: true,
    numeralType: true,
    pronounType: true,
    mood: true,
    tense: true,
    aspect: true,
    person: true,
    case: true,
    number: true,
    gender: true,
    degree: true,
    negation: true,
    deprecative: true,
};

const ORDERS: Readonly<Record<string, Readonly<Record<string, number>>>> = {
    part: PART_ORDER,
    case: CASE_ORDER,
    number: NUMBER_ORDER,
    gender: GENDER_ORDER,
    person: PERSON_ORDER,
    tense: TENSE_ORDER,
    mood: MOOD_ORDER,
    aspect: ASPECT_ORDER,
    degree: DEGREE_ORDER,
    verbForm: VERB_FORM_ORDER,
    numeralType: NUMERAL_TYPE_ORDER,
    pronounType: PRONOUN_TYPE_ORDER,
};

describe("the tagset orders", () => {
    it("ranks the terms of every dimension in declaration order from zero", () => {
        for (const [dimension, order] of Object.entries(ORDERS)) {
            const ranks = Object.values(order);
            expect(ranks, dimension).toEqual(ranks.map((_, index) => index));
        }
    });

    it("keeps the traditional Polish order of the school dimensions", () => {
        expect(Object.keys(CASE_ORDER)[0]).toBe("mianownik");
        expect(Object.keys(CASE_ORDER).at(-1)).toBe("wołacz");
        expect(Object.keys(NUMBER_ORDER)).toEqual(["pojedyncza", "mnoga"]);
        expect(Object.keys(DEGREE_ORDER)).toEqual(["równy", "wyższy", "najwyższy"]);
        expect(Object.keys(PERSON_ORDER)).toEqual(["pierwsza", "druga", "trzecia"]);
    });
});

describe("DIMENSION_ORDER", () => {
    it("carries every dimension of the tagset exactly once", () => {
        expect([...DIMENSION_ORDER].sort()).toEqual(Object.keys(EVERY_DIMENSION).sort());
    });
});

describe("termsOn", () => {
    it("reads the terms of one dimension in their canonical order", () => {
        const tags = someInflection({ cases: ["biernik", "mianownik"], number: "mnoga", deprecative: true });
        expect(termsOn(tags, "case")).toEqual(["mianownik", "biernik"]);
        expect(termsOn(tags, "number")).toEqual(["mnoga"]);
        expect(termsOn(tags, "deprecative")).toEqual([DEPRECATIVE_TERM]);
    });

    it("reads a dimension the bundle leaves open as no terms", () => {
        const tags = someInflection({ negation: false });
        expect(termsOn(tags, "gender")).toEqual([]);
        expect(termsOn(tags, "negation")).toEqual([]);
    });
});

describe("compareInflections", () => {
    it("ranks bundles by the first dimension they differ on", () => {
        const nominative = someInflection({ cases: ["mianownik"], number: "mnoga" });
        const genitive = someInflection({ cases: ["dopełniacz"], number: "pojedyncza" });
        expect(compareInflections(nominative, genitive)).toBeLessThan(0);
        expect(compareInflections(genitive, nominative)).toBeGreaterThan(0);
    });

    it("puts a bundle that leaves a dimension open before one that states it", () => {
        const plain = someInflection({ cases: ["mianownik"] });
        const deprecative = someInflection({ cases: ["mianownik"], deprecative: true });
        expect(compareInflections(plain, deprecative)).toBeLessThan(0);
    });

    it("ranks equal bundles together", () => {
        expect(compareInflections(someInflection({ person: "druga" }), someInflection({ person: "druga" }))).toBe(0);
    });
});

describe("inOrder", () => {
    it("sorts terms by their rank", () => {
        const cases: readonly Case[] = ["biernik", "wołacz", "mianownik", "dopełniacz"];
        expect(inOrder(cases, CASE_ORDER)).toEqual(["mianownik", "dopełniacz", "biernik", "wołacz"]);
    });

    it("leaves the given terms untouched", () => {
        const cases: readonly Case[] = ["biernik", "mianownik"];
        inOrder(cases, CASE_ORDER);
        expect(cases).toEqual(["biernik", "mianownik"]);
    });

    it("sorts nothing into nothing", () => {
        expect(inOrder([], CASE_ORDER)).toEqual([]);
    });
});
