import { describe, expect, it } from "vitest";

import type { AlphabetPreset, DistributionPreset } from "../../../src/api/tables";
import { bagTotal, categoriesOf, letterRows } from "../../../src/play/rules/letters";

const ALPHABET: AlphabetPreset = {
    name: "tiny",
    order: ["A", "B", "C"],
    dictionaries: ["sjp"],
    classes: [
        { value: 1, category: "yellow", letters: ["A"] },
        { value: 3, category: "blue", letters: ["B", "C"] },
    ],
};

const DISTRIBUTION: DistributionPreset = {
    name: "tiny",
    counts: { "9": ["A"], "2": ["B", "C"] },
};

describe("letterRows", () => {
    it("expands the alphabet in its own order", () => {
        const rows = letterRows(ALPHABET, DISTRIBUTION, {});
        expect(rows.map((row) => row.symbol)).toEqual(["A", "B", "C"]);
        expect(rows.map((row) => row.value)).toEqual([1, 3, 3]);
        expect(rows.map((row) => row.count)).toEqual([9, 2, 2]);
        expect(rows.map((row) => row.category)).toEqual(["yellow", "blue", "blue"]);
        expect(rows.every((row) => !row.changed)).toBe(true);
    });

    it("marks the letters an adjustment touches and leaves the rest", () => {
        const rows = letterRows(ALPHABET, DISTRIBUTION, { B: { value: 12, count: 3 } });
        const changed = rows.find((row) => row.symbol === "B");
        expect(changed).toEqual({ symbol: "B", value: 12, category: "blue", count: 3, changed: true });
        expect(rows.find((row) => row.symbol === "C")?.value).toBe(3);
    });

    it("adds a letter the alphabet lacks at the end", () => {
        const rows = letterRows(ALPHABET, DISTRIBUTION, {
            Q: { value: 8, category: "red", count: 1 },
        });
        expect(rows.at(-1)).toEqual({
            symbol: "Q",
            value: 8,
            category: "red",
            count: 1,
            changed: true,
        });
    });

    it("counts the whole bag and names the categories it carries", () => {
        const rows = letterRows(ALPHABET, DISTRIBUTION, {});
        expect(bagTotal(rows, 2)).toBe(15);
        expect(categoriesOf(rows)).toEqual(["yellow", "blue"]);
    });
});
