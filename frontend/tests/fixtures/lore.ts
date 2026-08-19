import type { InflectedForm, Inflection, LoreReading, WordLore } from "../../src/api/lore";
import { inflectedBy } from "../../src/play/lore/bundle";

export function someInflection(overrides: Partial<Inflection> = {}): Inflection {
    return inflectedBy(overrides);
}

export function aForm(overrides: Partial<InflectedForm> = {}): InflectedForm {
    return { text: "PIŁA", tags: someInflection(), playable: true, ...overrides };
}

export function aReading(overrides: Partial<LoreReading> = {}): LoreReading {
    return {
        lexeme: "rzeczownik:PIŁA:SF",
        part: "rzeczownik",
        base: "PIŁA",
        forms: [aForm()],
        ...overrides,
    };
}

export function aLore(overrides: Partial<WordLore> = {}): WordLore {
    return { word: "PIŁA", playable: true, readings: [aReading()], ...overrides };
}
