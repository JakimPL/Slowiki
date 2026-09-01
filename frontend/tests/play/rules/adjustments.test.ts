import { describe, expect, it } from "vitest";

import { withCategory, withLetter } from "../../../src/play/rules/adjustments";
import type { LetterRow } from "../../../src/play/rules/letters";

const STANDARD: readonly LetterRow[] = [
    { symbol: "A", value: 1, category: "yellow", count: 9, changed: false },
    { symbol: "B", value: 3, category: "blue", count: 2, changed: false },
    { symbol: "C", value: 3, category: "blue", count: 2, changed: false },
];

describe("withLetter", () => {
    it("states only what stands apart from the standard", () => {
        expect(withLetter({}, STANDARD, "A", { value: 4 })).toEqual({ A: { value: 4 } });
        expect(withLetter({}, STANDARD, "A", { value: 1 })).toEqual({});
    });

    it("keeps the fields already adjusted while another changes", () => {
        const held = withLetter({}, STANDARD, "A", { value: 4 });
        expect(withLetter(held, STANDARD, "A", { count: 3 })).toEqual({
            A: { value: 4, count: 3 },
        });
    });

    it("drops a letter whose every field returns to the standard", () => {
        const held = withLetter(withLetter({}, STANDARD, "A", { value: 4 }), STANDARD, "A", {
            count: 3,
        });
        const back = withLetter(withLetter(held, STANDARD, "A", { value: 1 }), STANDARD, "A", {
            count: 9,
        });
        expect(back).toEqual({});
    });

    it("leaves the other letters alone", () => {
        const held = withLetter({ B: { value: 5 } }, STANDARD, "A", { value: 4 });
        expect(held).toEqual({ A: { value: 4 }, B: { value: 5 } });
    });

    it("passes over a letter the alphabet lacks", () => {
        expect(withLetter({}, STANDARD, "Q", { value: 4 })).toEqual({});
    });
});

describe("withCategory", () => {
    it("sets the points of a whole color at once", () => {
        expect(withCategory({}, STANDARD, "blue", 6)).toEqual({
            B: { value: 6 },
            C: { value: 6 },
        });
    });

    it("clears a color put back to its standard points", () => {
        const held = withCategory({}, STANDARD, "blue", 6);
        expect(withCategory(held, STANDARD, "blue", 3)).toEqual({});
    });
});
