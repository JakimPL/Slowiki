import type { RuleChanges } from "./changes";

export interface SavedPreset {
    readonly id: string;
    readonly label: string;
    readonly origin: string;
    readonly changes: RuleChanges;
    readonly saved: number;
}

export interface PresetBook {
    readonly presets: readonly SavedPreset[];
    readonly last: string | null;
}

export const EMPTY_BOOK: PresetBook = { presets: [], last: null };

export function withPreset(book: PresetBook, preset: SavedPreset): PresetBook {
    const kept = book.presets.filter((held) => held.id !== preset.id);
    return { presets: [preset, ...kept], last: preset.id };
}

export function withoutPreset(book: PresetBook, id: string): PresetBook {
    return {
        presets: book.presets.filter((held) => held.id !== id),
        last: book.last === id ? null : book.last,
    };
}

export function lastUsed(book: PresetBook, entry: string): PresetBook {
    return { presets: book.presets, last: entry };
}

export function presetOf(book: PresetBook, id: string): SavedPreset | null {
    return book.presets.find((held) => held.id === id) ?? null;
}
