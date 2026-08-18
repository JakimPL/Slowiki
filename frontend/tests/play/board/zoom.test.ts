import { describe, expect, it } from "vitest";

import { MAX_SCALE, MIN_SCALE, zoomed } from "../../../src/play/board/zoom";

describe("zoomed", () => {
    it("reads the fitted board as unzoomed", () => {
        expect(zoomed(MIN_SCALE)).toBe(false);
    });

    it("holds the fitted reading through the float noise a pinch leaves behind", () => {
        expect(zoomed(1.000001)).toBe(false);
        expect(zoomed(0.9999)).toBe(false);
    });

    it("reads any real magnification as zoomed", () => {
        expect(zoomed(1.2)).toBe(true);
        expect(zoomed(MAX_SCALE)).toBe(true);
    });

    it("lets the board grow to three times its fitted size", () => {
        expect(MIN_SCALE).toBe(1);
        expect(MAX_SCALE).toBe(3);
    });
});
