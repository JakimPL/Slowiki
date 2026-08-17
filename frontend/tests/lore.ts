import type { InflectedForm, Inflection, LoreReading, WordLore } from "../src/api/lore";

export function someInflection(overrides: Partial<Inflection> = {}): Inflection {
    return {
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
        ...overrides,
    };
}

export function aForm(overrides: Partial<InflectedForm> = {}): InflectedForm {
    return { text: "PIŁA", tags: someInflection(), playable: true, ...overrides };
}

export function aReading(overrides: Partial<LoreReading> = {}): LoreReading {
    return {
        lexeme: "rzeczownik:PIŁA:SF",
        part: "rzeczownik",
        base: "piła",
        forms: [aForm()],
        ...overrides,
    };
}

export function aLore(overrides: Partial<WordLore> = {}): WordLore {
    return { word: "PIŁA", playable: true, readings: [aReading()], ...overrides };
}
