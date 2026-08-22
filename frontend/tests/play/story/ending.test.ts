import { describe, expect, it } from "vitest";

import { finished, unresolved } from "../../../src/play/story/ending";

describe("ending", () => {
    it("counts a played-out game and an abandoned one as finished", () => {
        expect(finished("game_over")).toBe(true);
        expect(finished("unresolved")).toBe(true);
        expect(finished("turn")).toBe(false);
    });

    it("tells an abandoned game from a played-out one", () => {
        expect(unresolved("unresolved")).toBe(true);
        expect(unresolved("game_over")).toBe(false);
        expect(unresolved("turn")).toBe(false);
    });
});
