import { describe, expect, it } from "vitest";

import type { ClockView } from "../../../src/api/views";
import { remainingFor, remainingSeconds, skewOf, urgencyOf } from "../../../src/play/clock/clock";
import { clockCaption } from "../../../src/table/strings";

const CLOCK: ClockView = { server_time: 1000, deadline: 1090, seat: 0, remaining: {} };
const BUDGETED: ClockView = { server_time: 1000, deadline: 1270, seat: 0, remaining: { 0: 270, 1: 300 } };

describe("clock", () => {
    it("corrects the countdown for clock skew", () => {
        const skew = skewOf(CLOCK, 500);
        expect(skew).toBe(500);
        expect(remainingSeconds(CLOCK, skew, 500)).toBe(90);
        expect(remainingSeconds(CLOCK, skew, 560)).toBe(30);
        expect(remainingSeconds(CLOCK, skew, 700)).toBe(0);
    });

    it("runs the thinking seat's clock and rests the others", () => {
        expect(remainingFor(BUDGETED, 0, 265)).toBe(265);
        expect(remainingFor(BUDGETED, 1, 265)).toBe(300);
        expect(remainingFor(CLOCK, 1, 90)).toBeNull();
    });

    it("grades urgency by the time left", () => {
        expect(urgencyOf(180)).toBe("calm");
        expect(urgencyOf(45)).toBe("low");
        expect(urgencyOf(9)).toBe("critical");
    });

    it("prints a chess-style caption", () => {
        expect(clockCaption(90)).toBe("1:30");
        expect(clockCaption(5.8)).toBe("0:05");
        expect(clockCaption(0)).toBe("0:00");
        expect(clockCaption(-3)).toBe("0:00");
    });
});
