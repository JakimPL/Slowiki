import type { ClockView } from "../api/views";

export type Urgency = "calm" | "low" | "critical";

const LOW_FRACTION = 0.25;
const CRITICAL_SECONDS = 10;

export function skewOf(clock: ClockView, receivedAtSeconds: number): number {
    return clock.server_time - receivedAtSeconds;
}

export function remainingSeconds(clock: ClockView, skew: number, nowSeconds: number): number {
    return Math.max(0, clock.deadline - (nowSeconds + skew));
}

export function urgencyOf(remaining: number, perTurnSeconds: number): Urgency {
    if (remaining <= CRITICAL_SECONDS) {
        return "critical";
    }
    if (remaining <= perTurnSeconds * LOW_FRACTION) {
        return "low";
    }
    return "calm";
}
