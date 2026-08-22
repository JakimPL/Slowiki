import type { PositionView } from "../../api/views";

export type Phase = PositionView["phase"];

export function finished(phase: Phase): boolean {
    return phase === "game_over" || phase === "unresolved";
}

export function unresolved(phase: Phase): boolean {
    return phase === "unresolved";
}
