import { describe, expect, it } from "vitest";

import type { ClockView } from "../src/api/views";
import { remainingSeconds, skewOf, urgencyOf } from "../src/play/clock";
import { clockCaption } from "../src/table/strings";

const CLOCK: ClockView = { server_time: 1000, deadline: 1090, seat: 0, per_turn_seconds: 90 };

describe("clock", () => {
    it("corrects the countdown for clock skew", () => {
        const skew = skewOf(CLOCK, 500);
        expect(skew).toBe(500);
        expect(remainingSeconds(CLOCK, skew, 500)).toBe(90);
        expect(remainingSeconds(CLOCK, skew, 560)).toBe(30);
        expect(remainingSeconds(CLOCK, skew, 700)).toBe(0);
    });

    it("grades urgency from the remaining share", () => {
        expect(urgencyOf(80, 90)).toBe("calm");
        expect(urgencyOf(20, 90)).toBe("low");
        expect(urgencyOf(9, 90)).toBe("critical");
    });

    it("prints a chess-style caption", () => {
        expect(clockCaption(90)).toBe("1:30");
        expect(clockCaption(5.8)).toBe("0:05");
        expect(clockCaption(0)).toBe("0:00");
        expect(clockCaption(-3)).toBe("0:00");
    });
});
