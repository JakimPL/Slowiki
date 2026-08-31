import { describe, expect, it } from "vitest";

import { typedValue } from "../../../src/play/rules/typed";

describe("typedValue", () => {
    it("takes a number the range holds", () => {
        expect(typedValue("37", 5, 3600)).toBe(37);
        expect(typedValue(" 120 ", 5, 3600)).toBe(120);
    });

    it("clamps a number the range refuses", () => {
        expect(typedValue("9999", 5, 3600)).toBe(3600);
        expect(typedValue("0", 5, 3600)).toBe(5);
    });

    it("rounds what is typed to a whole number", () => {
        expect(typedValue("7.6", 0, 99)).toBe(8);
    });

    it("keeps the standing value where what is typed is no number", () => {
        expect(typedValue("abc", 5, 3600)).toBeNull();
        expect(typedValue("", 5, 3600)).toBeNull();
        expect(typedValue("  ", 5, 3600)).toBeNull();
    });
});
