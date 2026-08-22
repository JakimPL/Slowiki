import type { WordStatus } from "./feedback";

export interface WordChip {
    readonly text: string;
    readonly points: number;
    readonly status: WordStatus;
}

export function wordRefused(chips: readonly WordChip[]): boolean {
    return chips.some((chip) => chip.status === "invalid");
}
