import type { TableTimeRequest } from "../../api/tables";

export const TURN_BUDGETS: readonly number[] = [60, 120, 300, 600, 900, 1800, 3600];
export const MOVE_INCREMENTS: readonly number[] = [0, 5, 10, 15, 30, 60];

export interface TimeChoice {
    readonly totalSeconds: number | null;
    readonly incrementSeconds: number;
}

export const UNTIMED: TimeChoice = { totalSeconds: null, incrementSeconds: 0 };

export function timeRequestOf(choice: TimeChoice): TableTimeRequest | null {
    if (choice.totalSeconds === null) {
        return null;
    }
    return { total_seconds: choice.totalSeconds, increment_seconds: choice.incrementSeconds };
}
