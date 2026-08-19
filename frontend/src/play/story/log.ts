import type { EventView, PlayRecord, PositionView } from "../../api/views";
import type { ScoredWord } from "../board/scoring";

export type LogKind = "play" | "exchange" | "pass" | "premove-returned";

export interface LogEntry {
    readonly seq: number;
    readonly actor: number;
    readonly kind: LogKind;
    readonly words: readonly ScoredWord[];
    readonly points: number | null;
    readonly reason: string | null;
}

export const LOG_LIMIT = 20;

export function logEntryOf(event: EventView, before: PositionView): LogEntry | null {
    const actor = event.actor;
    if (actor === null) {
        return null;
    }
    if (event.kind === "premove_discarded") {
        return {
            seq: event.seq,
            actor,
            kind: "premove-returned",
            words: [],
            points: null,
            reason: event.reason,
        };
    }
    if (event.kind !== "move") {
        return null;
    }
    const played = event.position.last_play;
    if (played !== null && !samePlay(played, before.last_play)) {
        return { seq: event.seq, actor, kind: "play", words: played.words, points: played.points, reason: null };
    }
    if (countOf(event.position.exchange_counts, actor) > countOf(before.exchange_counts, actor)) {
        return { seq: event.seq, actor, kind: "exchange", words: [], points: null, reason: null };
    }
    if (event.position.consecutive_passes > before.consecutive_passes) {
        return { seq: event.seq, actor, kind: "pass", words: [], points: null, reason: null };
    }
    return null;
}

export function appendedLog(log: readonly LogEntry[], entry: LogEntry | null): readonly LogEntry[] {
    if (entry === null) {
        return log;
    }
    return [...log, entry].slice(-LOG_LIMIT);
}

function samePlay(left: PlayRecord, right: PlayRecord | null): boolean {
    return right !== null && left.turn_number === right.turn_number && left.player === right.player;
}

function countOf(counts: Record<string, number>, seat: number): number {
    return counts[String(seat)] ?? 0;
}
