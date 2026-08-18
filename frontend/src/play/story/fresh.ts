import type { PlayRecord } from "../../api/views";

export interface FreshMark {
    readonly ordinal: number;
    readonly waving: boolean;
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
