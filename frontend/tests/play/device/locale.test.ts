import { describe, expect, it } from "vitest";

import {
    knownLocale,
    LOCALE_STORAGE_KEY,
    nextLocale,
    preferredLocale,
    rememberLocale,
    storedLocale,
} from "../../../src/play/device/locale";

function aStorage(initial: Record<string, string> = {}): {
    getItem: (key: string) => string | null;
    setItem: (key: string, value: string) => void;
    entries: Map<string, string>;
} {
    const entries = new Map(Object.entries(initial));
    return {
        getItem: (key): string | null => entries.get(key) ?? null,
        setItem: (key, value): void => {
            entries.set(key, value);
        },
        entries,
    };
}

describe("locale", () => {
    it("recognizes a catalogue locale and refuses the rest", () => {
        expect(knownLocale("en")).toBe("en");
        expect(knownLocale("pl")).toBe("pl");
        expect(knownLocale("kl")).toBeNull();
        expect(knownLocale(null)).toBeNull();
    });

    it("reads a stored choice", () => {
        expect(storedLocale(aStorage({ [LOCALE_STORAGE_KEY]: "en" }))).toBe("en");
        expect(storedLocale(aStorage())).toBeNull();
    });

    it("prefers the stored choice over the browser languages", () => {
        expect(preferredLocale("en", ["pl-PL"])).toBe("en");
    });

    it("reads the browser languages by their primary subtag", () => {
        expect(preferredLocale(null, ["PL-pl"])).toBe("pl");
        expect(preferredLocale(null, ["kl", "en-US"])).toBe("en");
    });

    it("falls back to the reference locale", () => {
        expect(preferredLocale(null, [])).toBe("en");
        expect(preferredLocale(null, ["kl"])).toBe("en");
    });

    it("cycles through the catalogue locales", () => {
        expect(nextLocale("en")).toBe("pl");
        expect(nextLocale("pl")).toBe("en");
    });

    it("remembers the choice", () => {
        const storage = aStorage();
        rememberLocale("pl", storage);
        expect(storage.entries.get(LOCALE_STORAGE_KEY)).toBe("pl");
    });
});
