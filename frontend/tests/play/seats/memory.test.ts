import { describe, expect, it } from "vitest";

import { forgetSeat, rememberSeat, SEAT_STORAGE_KEY, storedSeat } from "../../../src/play/seats/memory";
import { fragmentFor } from "../../../src/play/seats/session";
import { aStorage } from "../../fixtures/storage";

const SEATED = fragmentFor("abc123", "tok-1", "KWPZTR", 1);

describe("seat memory", () => {
    it("hands back the seat this tab arrived at", () => {
        const storage = aStorage();
        rememberSeat(SEATED, storage);
        expect(storage.entries.get(SEAT_STORAGE_KEY)).toBe(SEATED);
        expect(storedSeat(storage)).toBe(SEATED);
    });

    it("holds nothing before an arrival", () => {
        expect(storedSeat(aStorage())).toBeNull();
    });

    it("keeps only a fragment carrying credentials", () => {
        expect(storedSeat(aStorage({ [SEAT_STORAGE_KEY]: "#table=abc123&code=KWPZTR" }))).toBeNull();
        expect(storedSeat(aStorage({ [SEAT_STORAGE_KEY]: "" }))).toBeNull();
    });

    it("forgets the seat on the player's word", () => {
        const storage = aStorage({ [SEAT_STORAGE_KEY]: SEATED });
        forgetSeat(storage);
        expect(storedSeat(storage)).toBeNull();
    });

    it("replaces the seat when the tab arrives at another table", () => {
        const storage = aStorage({ [SEAT_STORAGE_KEY]: SEATED });
        const next = fragmentFor("def456", "tok-2", null, 0);
        rememberSeat(next, storage);
        expect(storedSeat(storage)).toBe(next);
    });
});
