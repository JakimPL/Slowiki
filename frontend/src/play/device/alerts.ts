const BUZZ_PULSE_MS = 80;
const BUZZ_GAP_MS = 40;

export const TURN_BUZZ: readonly number[] = [BUZZ_PULSE_MS, BUZZ_GAP_MS, BUZZ_PULSE_MS];

export interface Buzzer {
    readonly vibrate?: (pattern: number[]) => boolean;
}

export function retitled(base: string, acting: boolean): string {
    return acting ? `● ${base} — your turn` : base;
}

export function buzzed(target: Buzzer, pattern: readonly number[]): void {
    if (typeof target.vibrate === "function") {
        target.vibrate([...pattern]);
    }
}
