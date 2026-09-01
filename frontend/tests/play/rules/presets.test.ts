import { describe, expect, it } from "vitest";

import type { SavedPreset } from "../../../src/play/rules/preset";
import { EMPTY_BOOK, lastUsed, presetOf, withoutPreset, withPreset } from "../../../src/play/rules/preset";
import {
    newPresetId,
    parsedPresets,
    PRESETS_STORAGE_KEY,
    rememberPresets,
    storedPresets,
} from "../../../src/play/rules/storage";

function aPreset(overrides: Partial<SavedPreset> = {}): SavedPreset {
    return {
        id: "preset-1",
        label: "House rules",
        origin: "literaki",
        changes: { seats: 4 },
        saved: 1000,
        ...overrides,
    };
}

class FakeStorage {
    private held = new Map<string, string>();

    getItem(key: string): string | null {
        return this.held.get(key) ?? null;
    }

    setItem(key: string, value: string): void {
        this.held.set(key, value);
    }
}

describe("the preset book", () => {
    it("puts a saved record at the front and remembers it as the last used", () => {
        const book = withPreset(EMPTY_BOOK, aPreset());
        expect(book.presets.map((preset) => preset.id)).toEqual(["preset-1"]);
        expect(book.last).toBe("preset-1");
    });

    it("saving under the same id replaces the record", () => {
        const first = withPreset(EMPTY_BOOK, aPreset());
        const renamed = withPreset(first, aPreset({ label: "Ours" }));
        expect(renamed.presets).toHaveLength(1);
        expect(presetOf(renamed, "preset-1")?.label).toBe("Ours");
    });

    it("deleting a record forgets it as the last used", () => {
        const book = withoutPreset(withPreset(EMPTY_BOOK, aPreset()), "preset-1");
        expect(book.presets).toEqual([]);
        expect(book.last).toBeNull();
    });

    it("remembers whichever entry was last used", () => {
        expect(lastUsed(EMPTY_BOOK, "scrabble").last).toBe("scrabble");
    });
});

describe("preset storage", () => {
    it("carries a book through storage under its own key", () => {
        const storage = new FakeStorage();
        rememberPresets(withPreset(EMPTY_BOOK, aPreset()), storage);
        expect(storage.getItem(PRESETS_STORAGE_KEY)).not.toBeNull();
        const read = storedPresets(storage);
        expect(read.presets[0]?.changes).toEqual({ seats: 4 });
        expect(read.last).toBe("preset-1");
    });

    it("holds nothing before anything is saved", () => {
        expect(storedPresets(new FakeStorage())).toEqual(EMPTY_BOOK);
    });

    it("survives a document another version wrote", () => {
        const book = parsedPresets(
            JSON.stringify({
                presets: [
                    { id: "a", label: "Mine", origin: "literaki", changes: { seats: 3 }, extra: 1 },
                    { label: "nameless", origin: "literaki" },
                    "rubbish",
                ],
                last: "a",
                unknown: true,
            }),
        );
        expect(book.presets.map((preset) => preset.id)).toEqual(["a"]);
        expect(book.presets[0]?.changes).toEqual({ seats: 3 });
        expect(book.last).toBe("a");
    });

    it("survives text that is not a document at all", () => {
        expect(parsedPresets("{oh no")).toEqual(EMPTY_BOOK);
        expect(parsedPresets("[]")).toEqual(EMPTY_BOOK);
    });

    it("mints an identifier for every saved record", () => {
        expect(newPresetId()).not.toBe(newPresetId());
    });
});
