import { describe, expect, it } from "vitest";

import type { Case } from "../src/api/lore";
import {
    ASPECT_ORDER,
    CASE_ORDER,
    DEGREE_ORDER,
    GENDER_ORDER,
    inOrder,
    MOOD_ORDER,
    NUMBER_ORDER,
    NUMERAL_TYPE_ORDER,
    PART_ORDER,
    PERSON_ORDER,
    PRONOUN_TYPE_ORDER,
    TENSE_ORDER,
    VERB_FORM_ORDER,
} from "../src/play/tagset";

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
