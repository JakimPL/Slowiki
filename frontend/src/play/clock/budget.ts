import type { ClockView } from "../../api/views";

export function outOfTime(clock: ClockView | null, seat: number | null, running: number | null): boolean {
    if (clock === null || seat === null) {
        return false;
    }
    if (banked(clock, seat)) {
        return true;
    }
    return clock.seat === seat && running !== null && running <= 0;
}

function banked(clock: ClockView, seat: number): boolean {
    const left = clock.remaining[String(seat)];
    return left !== undefined && left <= 0;
}
