import type { Inflection } from "../api/lore";

export const NO_INFLECTION: Inflection = {
    cases: [],
    number: null,
    genders: [],
    person: null,
    tense: null,
    mood: null,
    aspects: [],
    degree: null,
    verb_form: null,
    numeral_type: null,
    pronoun_type: null,
    negation: null,
    deprecative: false,
};

export function inflectedBy(stated: Partial<Inflection>): Inflection {
    return { ...NO_INFLECTION, ...stated };
}
