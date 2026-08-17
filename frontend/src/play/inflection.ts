import type { Inflection } from "../api/lore";
import { ASPECT_ORDER, CASE_ORDER, GENDER_ORDER, inOrder } from "./tagset";

export type Dimension =
    | "verbForm"
    | "numeralType"
    | "pronounType"
    | "mood"
    | "tense"
    | "aspect"
    | "person"
    | "case"
    | "number"
    | "gender"
    | "degree"
    | "negation"
    | "deprecative";

export const NEGATED_TERM = "zaprzeczony";

export const DEPRECATIVE_TERM = "deprecjatywny";

const READING_ORDER: readonly Dimension[] = [
    "verbForm",
    "numeralType",
    "pronounType",
    "mood",
    "tense",
    "aspect",
    "person",
    "case",
    "number",
    "gender",
    "degree",
    "negation",
    "deprecative",
];

const TERMS_ON: Record<Dimension, (tags: Inflection) => readonly string[]> = {
    verbForm: (tags) => stated(tags.verb_form),
    numeralType: (tags) => stated(tags.numeral_type),
    pronounType: (tags) => stated(tags.pronoun_type),
    mood: (tags) => stated(tags.mood),
    tense: (tags) => stated(tags.tense),
    aspect: (tags) => inOrder(tags.aspects, ASPECT_ORDER),
    person: (tags) => stated(tags.person),
    case: (tags) => inOrder(tags.cases, CASE_ORDER),
    number: (tags) => stated(tags.number),
    gender: (tags) => inOrder(tags.genders, GENDER_ORDER),
    degree: (tags) => stated(tags.degree),
    negation: (tags) => (tags.negation === true ? [NEGATED_TERM] : []),
    deprecative: (tags) => (tags.deprecative ? [DEPRECATIVE_TERM] : []),
};

export function inflectionTerms(tags: Inflection, except: readonly Dimension[]): readonly string[] {
    const covered = new Set(except);
    return READING_ORDER.filter((dimension) => !covered.has(dimension)).flatMap((dimension) =>
        TERMS_ON[dimension](tags),
    );
}

function stated(term: string | null): readonly string[] {
    return term === null ? [] : [term];
}
