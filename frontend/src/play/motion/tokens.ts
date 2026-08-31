const SECOND_MS = 1000;
const SECONDS = "s";
const MILLISECONDS = "ms";
const EVEN = "linear";

export function durationOf(raw: string): number {
    const value = raw.trim();
    if (value.endsWith(MILLISECONDS)) {
        return positive(value.slice(0, -MILLISECONDS.length));
    }
    if (value.endsWith(SECONDS)) {
        return positive(value.slice(0, -SECONDS.length)) * SECOND_MS;
    }
    return 0;
}

export function easingOf(raw: string): string {
    const value = raw.trim();
    return value === "" ? EVEN : value;
}

function positive(digits: string): number {
    const parsed = Number(digits);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}
