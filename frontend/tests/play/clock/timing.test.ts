import { describe, expect, it } from "vitest";

import { MOVE_INCREMENTS, TURN_BUDGETS, UNTIMED } from "../../../src/play/clock/timing";

describe("timing", () => {
    it("offers minute budgets and second increments", () => {
        expect(TURN_BUDGETS[0]).toBe(60);
        expect(TURN_BUDGETS.at(-1)).toBe(3600);
        expect(MOVE_INCREMENTS[0]).toBe(0);
    });

    it("leaves a table untimed until a budget is chosen", () => {
        expect(UNTIMED.totalSeconds).toBeNull();
        expect(UNTIMED.incrementSeconds).toBe(0);
    });
});
