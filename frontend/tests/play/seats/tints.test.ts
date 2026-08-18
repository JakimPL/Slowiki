import { describe, expect, it } from "vitest";

import { PLAYER_TINTS, tintFor } from "../../../src/play/seats/tints";

const LNIANY_BANDS = ["#D9A226", "#67903F", "#38719B", "#AC4029", "#E0AB2B", "#7BA34C", "#4E86B4", "#C04E33"];

describe("PLAYER_TINTS", () => {
    it("offers eight distinct tints", () => {
        expect(PLAYER_TINTS).toHaveLength(8);
        expect(new Set(PLAYER_TINTS.map((tint) => tint.hex)).size).toBe(8);
    });

    it("stays apart from the category band hues", () => {
        const bands = new Set(LNIANY_BANDS.map((hex) => hex.toUpperCase()));
        for (const tint of PLAYER_TINTS) {
            expect(bands.has(tint.hex.toUpperCase())).toBe(false);
        }
    });
});

describe("tintFor", () => {
    it("assigns seats in order and wraps past eight", () => {
        expect(tintFor(0).name).toBe("rose");
        expect(tintFor(7).name).toBe("graphite");
        expect(tintFor(8).name).toBe("rose");
    });
});
