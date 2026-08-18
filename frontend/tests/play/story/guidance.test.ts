import { describe, expect, it } from "vitest";

import { guidanceFor } from "../../../src/play/story/guidance";

describe("guidanceFor", () => {
    it("hints at placing while a tile is lifted", () => {
        expect(guidanceFor("empty", true)).toBe("place");
        expect(guidanceFor("empty", false)).toBeNull();
    });

    it("passes structural verdicts through", () => {
        expect(guidanceFor("opening-short", false)).toBe("opening-short");
        expect(guidanceFor("off-center", true)).toBe("off-center");
        expect(guidanceFor("detached", false)).toBe("detached");
        expect(guidanceFor("scattered", false)).toBe("scattered");
        expect(guidanceFor("gapped", false)).toBe("gapped");
    });

    it("stays quiet when the play is ready", () => {
        expect(guidanceFor("playable", false)).toBeNull();
        expect(guidanceFor("playable", true)).toBeNull();
    });
});
