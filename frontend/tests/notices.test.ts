import { describe, expect, it } from "vitest";

import { NOTICE_STORAGE_KEY, noticeDue, rememberNotices, storedNotices } from "../src/play/notices";

function aStorage(): Storage & { readonly held: Map<string, string> } {
    const held = new Map<string, string>();
    return {
        held,
        length: 0,
        clear: () => undefined,
        key: () => null,
        getItem: (key: string) => held.get(key) ?? null,
        setItem: (key: string, value: string) => {
            held.set(key, value);
        },
        removeItem: (key: string) => {
            held.delete(key);
        },
    };
}

describe("notices", () => {
    it("remembers the choice across visits", () => {
        const storage = aStorage();
        expect(storedNotices(storage)).toBe(false);
        rememberNotices(true, storage);
        expect(storage.held.get(NOTICE_STORAGE_KEY)).toBe("on");
        expect(storedNotices(storage)).toBe(true);
        rememberNotices(false, storage);
        expect(storedNotices(storage)).toBe(false);
    });

    it("posts only for my turn on a resting tab with permission", () => {
        expect(noticeDue(true, true, true, "granted")).toBe(true);
        expect(noticeDue(false, true, true, "granted")).toBe(false);
        expect(noticeDue(true, false, true, "granted")).toBe(false);
        expect(noticeDue(true, true, false, "granted")).toBe(false);
        expect(noticeDue(true, true, true, "denied")).toBe(false);
    });
});
