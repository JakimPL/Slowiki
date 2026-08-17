import { describe, expect, it } from "vitest";

import { MOVE_INCREMENTS, timeRequestOf, TURN_BUDGETS, UNTIMED } from "../src/play/timing";

describe("timing", () => {
    it("offers minute budgets and second increments", () => {
        expect(TURN_BUDGETS[0]).toBe(60);
        expect(TURN_BUDGETS.at(-1)).toBe(3600);
        expect(MOVE_INCREMENTS[0]).toBe(0);
    });

    it("asks for a clock only when a budget is chosen", () => {
        expect(timeRequestOf(UNTIMED)).toBeNull();
        expect(timeRequestOf({ totalSeconds: 600, incrementSeconds: 15 })).toEqual({
            total_seconds: 600,
            increment_seconds: 15,
        });
    });
});
