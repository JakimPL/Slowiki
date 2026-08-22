import { describe, expect, it } from "vitest";

import { loreFor } from "../../../src/play/lore/lore";
import { loreStateOf } from "../../../src/play/lore/readings";

describe("loreFor", () => {
    it("answers a refused word as absent", () => {
        expect(loreFor("ZQX", false)).toEqual({ word: "ZQX", playable: false, readings: [] });
        expect(loreStateOf(loreFor("ZQX", false))).toBe("absent");
    });

    it("answers a playable word as unclassified while no source is wired", () => {
        expect(loreFor("PIŁA", true)).toEqual({ word: "PIŁA", playable: true, readings: [] });
        expect(loreStateOf(loreFor("PIŁA", true))).toBe("unclassified");
    });

    it("claims no reading it cannot source", () => {
        for (const word of ["PICIA", "KOSA", "TRAWA", "MIŁOŚĆ"]) {
            expect(loreFor(word, true).readings, word).toEqual([]);
        }
    });
});
