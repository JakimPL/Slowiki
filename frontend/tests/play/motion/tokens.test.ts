import { describe, expect, it } from "vitest";

import { durationOf, easingOf } from "../../../src/play/motion/tokens";

describe("durationOf", () => {
    it("reads the step the stylesheet spends", () => {
        expect(durationOf("150ms")).toBe(150);
        expect(durationOf(" 150ms ")).toBe(150);
        expect(durationOf("0.15s")).toBe(150);
        expect(durationOf("2.6s")).toBe(2600);
    });

    it("stills the effect at a zeroed scale", () => {
        expect(durationOf("0s")).toBe(0);
        expect(durationOf("0ms")).toBe(0);
        expect(durationOf("none")).toBe(0);
        expect(durationOf("")).toBe(0);
    });
});

describe("easingOf", () => {
    it("reads the curve the stylesheet names", () => {
        expect(easingOf("ease")).toBe("ease");
        expect(easingOf(" ease-in-out ")).toBe("ease-in-out");
        expect(easingOf("cubic-bezier(0.2, 0.9, 0.3, 1.2)")).toBe("cubic-bezier(0.2, 0.9, 0.3, 1.2)");
    });

    it("holds an even pace where the sheet says nothing", () => {
        expect(easingOf("")).toBe("linear");
        expect(easingOf("   ")).toBe("linear");
    });
});
