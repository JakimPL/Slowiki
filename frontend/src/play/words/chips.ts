import type { WordStatus } from "./feedback";

export interface WordChip {
    readonly text: string;
    readonly points: number;
    readonly status: WordStatus;
}
