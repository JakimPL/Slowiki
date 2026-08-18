import type { ClockView } from "../../api/views";

export type Urgency = "calm" | "low" | "critical";

const LOW_SECONDS = 60;
const CRITICAL_SECONDS = 10;

export function skewOf(clock: ClockView, receivedAtSeconds: number): number {
    return clock.server_time - receivedAtSeconds;
}

export function remainingSeconds(clock: ClockView, skew: number, nowSeconds: number): number {
    return Math.max(0, clock.deadline - (nowSeconds + skew));
}

export function remainingFor(clock: ClockView, seat: number, running: number | null): number | null {
    if (clock.seat === seat) {
        return running;
    }
    return clock.remaining[String(seat)] ?? null;
}

export function urgencyOf(remaining: number): Urgency {
    if (remaining <= CRITICAL_SECONDS) {
        return "critical";
    }
    if (remaining <= LOW_SECONDS) {
        return "low";
    }
    return "calm";
}
