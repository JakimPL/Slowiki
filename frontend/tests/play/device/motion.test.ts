import { describe, expect, it } from "vitest";

import { knownMotion, nextMotion } from "../../../src/play/device/motion";

describe("motion", () => {
    it("recognizes the three choices and refuses the rest", () => {
        expect(knownMotion("system")).toBe("system");
        expect(knownMotion("calm")).toBe("calm");
        expect(knownMotion("still")).toBeNull();
        expect(knownMotion(null)).toBeNull();
    });

    it("cycles system, full, calm, system", () => {
        expect(nextMotion("system")).toBe("full");
        expect(nextMotion("full")).toBe("calm");
        expect(nextMotion("calm")).toBe("system");
    });
});
