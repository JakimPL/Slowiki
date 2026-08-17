import type { InflectedForm, LoreReading, WordLore } from "../api/lore";
import type { WordStatus } from "./feedback";

export type LoreState = "absent" | "unclassified" | "read";

export function loreStateOf(lore: WordLore): LoreState {
    if (!lore.playable) {
        return "absent";
    }
    return lore.readings.length === 0 ? "unclassified" : "read";
}

export function askedFormsOf(reading: LoreReading, word: string): readonly InflectedForm[] {
    return reading.forms.filter((form) => form.text === word);
}

export function readingByLexeme(lore: WordLore, lexeme: string): LoreReading | null {
    return lore.readings.find((reading) => reading.lexeme === lexeme) ?? null;
}

export function firstLexeme(lore: WordLore): string | null {
    return lore.readings[0]?.lexeme ?? null;
}

export function assumedPlayable(status: WordStatus): boolean {
    return status !== "invalid";
}
