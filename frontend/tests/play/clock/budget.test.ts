import { describe, expect, it } from "vitest";

import type { ClockView } from "../../../src/api/views";
import { outOfTime } from "../../../src/play/clock/budget";

const PER_TURN: ClockView = { server_time: 1000, deadline: 1090, seat: 0, remaining: {} };
const BUDGETED: ClockView = { server_time: 1000, deadline: 1030, seat: 0, remaining: { 0: 30, 1: 0 } };

describe("budget", () => {
    it("leaves a seat with time in play", () => {
        expect(outOfTime(BUDGETED, 0, 12)).toBe(false);
        expect(outOfTime(PER_TURN, 0, 12)).toBe(false);
    });

    it("takes the thinking seat out when the countdown reaches zero", () => {
        expect(outOfTime(BUDGETED, 0, 0)).toBe(true);
    });

    it("takes a seat out on a banked budget of nothing", () => {
        expect(outOfTime(BUDGETED, 1, 12)).toBe(true);
    });

    it("keeps a per-turn seat in play between turns", () => {
        expect(outOfTime(PER_TURN, 1, 0)).toBe(false);
    });

    it("reads the banked budget before the countdown has ticked", () => {
        expect(outOfTime(BUDGETED, 1, null)).toBe(true);
        expect(outOfTime(BUDGETED, 0, null)).toBe(false);
    });

    it("holds no view on a table without a clock or a seat", () => {
        expect(outOfTime(null, 0, 0)).toBe(false);
        expect(outOfTime(BUDGETED, null, 0)).toBe(false);
    });
});
