export const HEARTBEAT_MILLISECONDS = 15000;
export const SILENCE_LIMIT_MILLISECONDS = HEARTBEAT_MILLISECONDS * 2 + 5000;
export const WATCH_INTERVAL_MILLISECONDS = 5000;

export function silent(lastBeat: number, now: number): boolean {
    return now - lastBeat > SILENCE_LIMIT_MILLISECONDS;
}
