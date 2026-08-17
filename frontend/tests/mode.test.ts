import { describe, expect, it } from "vitest";

import { MODE_STORAGE_KEY, nextMode, rememberMode, storedMode } from "../src/play/mode";

function aStorage(initial: Record<string, string> = {}): {
    getItem: (key: string) => string | null;
    setItem: (key: string, value: string) => void;
    removeItem: (key: string) => void;
    entries: Map<string, string>;
} {
    const entries = new Map(Object.entries(initial));
    return {
        getItem: (key): string | null => entries.get(key) ?? null,
        setItem: (key, value): void => {
            entries.set(key, value);
        },
        removeItem: (key): void => {
            entries.delete(key);
        },
        entries,
    };
}

describe("mode", () => {
    it("reads a stored override and falls back to system", () => {
        expect(storedMode(aStorage())).toBe("system");
        expect(storedMode(aStorage({ [MODE_STORAGE_KEY]: "dark" }))).toBe("dark");
        expect(storedMode(aStorage({ [MODE_STORAGE_KEY]: "nonsense" }))).toBe("system");
    });

    it("cycles system, light, dark, system", () => {
        expect(nextMode("system")).toBe("light");
        expect(nextMode("light")).toBe("dark");
        expect(nextMode("dark")).toBe("system");
    });

    it("remembers overrides and clears the system choice", () => {
        const storage = aStorage({ [MODE_STORAGE_KEY]: "dark" });
        rememberMode("light", storage);
        expect(storage.entries.get(MODE_STORAGE_KEY)).toBe("light");
        rememberMode("system", storage);
        expect(storage.entries.has(MODE_STORAGE_KEY)).toBe(false);
    });
});
