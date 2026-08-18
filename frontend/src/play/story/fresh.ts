import type { PlayRecord } from "../../api/views";
import { columnOf, rowOf } from "../board/board";

export interface FreshMark {
    readonly ordinal: number;
    readonly waving: boolean;
}

export interface FreshFrame {
    readonly row: number;
    readonly column: number;
    readonly rows: number;
    readonly columns: number;
}

export const BEFORE_ANY_TURN = -1;

const NO_MARKS: ReadonlyMap<number, FreshMark> = new Map();

export function freshMarks(
    play: PlayRecord | null,
    mySeat: number | null,
    acknowledged: number,
): ReadonlyMap<number, FreshMark> {
    if (play === null) {
        return NO_MARKS;
    }
    const waving = play.player !== mySeat && play.turn_number > acknowledged;
    const along = [...play.indices].sort((left, right) => left - right);
    return new Map(along.map((cell, ordinal) => [cell, { ordinal, waving }]));
}

export function freshFrame(play: PlayRecord | null, size: number): FreshFrame | null {
    if (play === null || play.indices.length === 0) {
        return null;
    }
    const rows = play.indices.map((cell) => rowOf(size, cell));
    const columns = play.indices.map((cell) => columnOf(size, cell));
    const row = Math.min(...rows);
    const column = Math.min(...columns);
    return {
        row,
        column,
        rows: Math.max(...rows) - row + 1,
        columns: Math.max(...columns) - column + 1,
    };
}
