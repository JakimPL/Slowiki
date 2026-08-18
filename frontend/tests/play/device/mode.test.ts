import { describe, expect, it } from "vitest";

import { knownMode, nextMode } from "../../../src/play/device/mode";

describe("mode", () => {
    it("recognizes the three choices and refuses the rest", () => {
        expect(knownMode("system")).toBe("system");
        expect(knownMode("dark")).toBe("dark");
        expect(knownMode("nonsense")).toBeNull();
        expect(knownMode(null)).toBeNull();
    });

    it("cycles system, light, dark, system", () => {
        expect(nextMode("system")).toBe("light");
        expect(nextMode("light")).toBe("dark");
        expect(nextMode("dark")).toBe("system");
    });
});
