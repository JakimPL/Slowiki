import { describe, expect, it } from "vitest";

import { NAME_STORAGE_KEY, rememberName, storedName } from "../src/play/identity";

interface FakeStorage {
    readonly held: Map<string, string>;
    readonly getItem: (key: string) => string | null;
    readonly setItem: (key: string, value: string) => void;
    readonly removeItem: (key: string) => void;
}

function fakeStorage(initial: Record<string, string>): FakeStorage {
    const held = new Map(Object.entries(initial));
    return {
        held,
        getItem: (key) => held.get(key) ?? null,
        setItem: (key, value) => {
            held.set(key, value);
        },
        removeItem: (key) => {
            held.delete(key);
        },
    };
}

describe("identity", () => {
    it("reads the remembered name and falls back to an empty one", () => {
        expect(storedName(fakeStorage({ [NAME_STORAGE_KEY]: "Ala" }))).toBe("Ala");
        expect(storedName(fakeStorage({}))).toBe("");
    });

    it("stores a chosen name and forgets a cleared one", () => {
        const storage = fakeStorage({ [NAME_STORAGE_KEY]: "Ala" });
        rememberName("Ola", storage);
        expect(storage.held.get(NAME_STORAGE_KEY)).toBe("Ola");
        rememberName(null, storage);
        expect(storage.held.has(NAME_STORAGE_KEY)).toBe(false);
    });
});
