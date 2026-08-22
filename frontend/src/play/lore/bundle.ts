import type { Inflection } from "../../api/lore";

export const NO_INFLECTION: Inflection = {
    cases: [],
    governed_case: null,
    numbers: [],
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
    qualities: [],
};

export function inflectedBy(stated: Partial<Inflection>): Inflection {
    return { ...NO_INFLECTION, ...stated };
}
