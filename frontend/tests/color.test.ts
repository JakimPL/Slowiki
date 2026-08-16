import { describe, expect, it } from "vitest";

import { mixHex } from "../src/table/color";

describe("mixHex", () => {
    it("returns the base at share zero", () => {
        expect(mixHex("#faf3e1", "#d9a226", 0)).toBe("#faf3e1");
    });

    it("returns the overlay at share one", () => {
        expect(mixHex("#faf3e1", "#d9a226", 1)).toBe("#d9a226");
    });

    it("blends channels linearly and rounds", () => {
        expect(mixHex("#000000", "#ffffff", 0.5)).toBe("#808080");
        expect(mixHex("#faf3e1", "#d9a226", 0.15)).toBe("#f5e7c5");
    });

    it("pads small channels to two digits", () => {
        expect(mixHex("#000000", "#0a0a0a", 0.5)).toBe("#050505");
    });
});
