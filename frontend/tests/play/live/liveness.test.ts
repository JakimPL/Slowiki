import { describe, expect, it } from "vitest";

import { HEARTBEAT_MILLISECONDS, SILENCE_LIMIT_MILLISECONDS, silent } from "../../../src/play/live/liveness";

describe("silent", () => {
    it("tolerates a single missed beat", () => {
        expect(silent(0, HEARTBEAT_MILLISECONDS * 2)).toBe(false);
    });

    it("calls a table dead once the silence outlasts the limit", () => {
        expect(silent(0, SILENCE_LIMIT_MILLISECONDS + 1)).toBe(true);
    });

    it("counts from the last beat, not from the start", () => {
        const beat = 1_000_000;
        expect(silent(beat, beat + SILENCE_LIMIT_MILLISECONDS)).toBe(false);
        expect(silent(beat, beat + SILENCE_LIMIT_MILLISECONDS + 1)).toBe(true);
    });
});
