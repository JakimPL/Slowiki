import { describe, expect, it } from "vitest";

import { entriesOf, entryOf, playableEntries } from "../../../src/play/rules/entry";
import { EMPTY_BOOK, withPreset } from "../../../src/play/rules/preset";
import { anOffering } from "../../fixtures/positions";

const OFFERINGS = [anOffering({ name: "literaki" }), anOffering({ name: "scrabble" })];

describe("entriesOf", () => {
    it("presents the schemes and the saved records as one list", () => {
        const book = withPreset(EMPTY_BOOK, {
            id: "preset-1",
            label: "House rules",
            origin: "literaki",
            changes: { seats: 4 },
            saved: 1,
        });
        const entries = entriesOf(OFFERINGS, book);
        expect(entries.map((entry) => entry.label)).toEqual(["literaki", "scrabble", "House rules"]);
        expect(entries.map((entry) => entry.saved)).toEqual([false, false, true]);
        expect(entryOf(entries, "preset-1")?.origin).toBe("literaki");
        expect(entryOf(entries, null)).toBeNull();
    });

    it("keeps a record whose scheme the server no longer offers out of the playable list", () => {
        const book = withPreset(EMPTY_BOOK, {
            id: "preset-2",
            label: "Old rules",
            origin: "retired",
            changes: {},
            saved: 1,
        });
        const entries = entriesOf(OFFERINGS, book);
        expect(entryOf(entries, "preset-2")?.offered).toBe(false);
        expect(playableEntries(entries).map((entry) => entry.id)).toEqual(["literaki", "scrabble"]);
    });

    it("resolves a scheme entry against itself with nothing changed", () => {
        const entries = entriesOf(OFFERINGS, EMPTY_BOOK);
        expect(entries[0]).toEqual({
            id: "literaki",
            label: "literaki",
            origin: "literaki",
            changes: {},
            saved: false,
            offered: true,
        });
    });
});
