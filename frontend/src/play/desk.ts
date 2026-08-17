import type { Board, Tile } from "../api/views";
import type { Arrangement } from "./arrangement";
import { EMPTY_ARRANGEMENT, movedBefore, reconciledArrangement } from "./arrangement";
import type { Draft, Pending } from "./draft";
import { EMPTY_DRAFT, laidDown, pendingAt, reconciledDraft, stamped, takenBack } from "./draft";
import type { Lift } from "./selection";
import { toggledLift } from "./selection";
import type { DeskSpot } from "./spot";
import type { Tray } from "./tray";
import { EMPTY_TRAY, parkedTray, reconciledTray, retrievedTray } from "./tray";

export interface Desk {
    readonly draft: Draft;
    readonly lift: Lift | null;
    readonly tray: Tray;
    readonly arrangement: Arrangement;
}

export const EMPTY_DESK: Desk = {
    draft: EMPTY_DRAFT,
    lift: null,
    tray: EMPTY_TRAY,
    arrangement: EMPTY_ARRANGEMENT,
};

export type DeskEffect =
    | { readonly kind: "lift"; readonly tile: Tile; readonly from: DeskSpot }
    | { readonly kind: "lay"; readonly cell: number; readonly tile: Tile; readonly letter: string | null }
    | { readonly kind: "relay"; readonly from: number; readonly to: number }
    | { readonly kind: "take-back"; readonly cell: number }
    | { readonly kind: "stamp"; readonly cell: number; readonly letter: string }
    | { readonly kind: "park"; readonly id: number; readonly before: number | null }
    | { readonly kind: "retrieve"; readonly id: number; readonly before: number | null }
    | { readonly kind: "reorder"; readonly id: number; readonly before: number | null }
    | { readonly kind: "arrange"; readonly arrangement: Arrangement }
    | { readonly kind: "recall" }
    | { readonly kind: "clear-lift" };

export function affected(desk: Desk, effect: DeskEffect): Desk {
    switch (effect.kind) {
        case "lift":
            return { ...desk, lift: toggledLift(desk.lift, effect.tile, effect.from) };
        case "lay":
            return laid(desk, effect.cell, effect.tile, effect.letter);
        case "relay":
            return relaid(desk, effect.from, effect.to);
        case "take-back":
            return takenBackFrom(desk, effect.cell);
        case "stamp":
            return { ...desk, draft: stamped(desk.draft, effect.cell, effect.letter) };
        case "park":
            return parked(desk, effect.id, effect.before);
        case "retrieve":
            return {
                ...desk,
                tray: retrievedTray(desk.tray, effect.id),
                arrangement: movedBefore(desk.arrangement, effect.id, effect.before),
                lift: liftWithout(desk.lift, effect.id),
            };
        case "reorder":
            return {
                ...desk,
                arrangement: movedBefore(desk.arrangement, effect.id, effect.before),
                lift: liftWithout(desk.lift, effect.id),
            };
        case "arrange":
            return { ...desk, arrangement: effect.arrangement };
        case "recall":
            return { ...desk, draft: EMPTY_DRAFT, lift: null };
        case "clear-lift":
            return { ...desk, lift: null };
    }
}

export function reconciledDesk(
    desk: Desk,
    rack: readonly Tile[] | null,
    board: Board,
    committed: ReadonlySet<number>,
): Desk {
    const draft = reconciledDraft(desk.draft, rack, board, committed);
    const tray = reconciledTray(desk.tray, rack);
    const arrangement = reconciledArrangement(desk.arrangement, rack);
    const lift = liftStillHeld(desk.lift, rack, committed) ? desk.lift : null;
    if (draft === desk.draft && tray === desk.tray && arrangement === desk.arrangement && lift === desk.lift) {
        return desk;
    }
    return { draft, lift, tray, arrangement };
}

function laid(desk: Desk, cell: number, tile: Tile, letter: string | null): Desk {
    if (pendingAt(desk.draft, cell) !== null) {
        return desk;
    }
    return {
        ...desk,
        draft: laidDown(desk.draft, { cell, tile, letter }),
        tray: retrievedTray(desk.tray, tile.identifier),
        lift: liftWithout(desk.lift, tile.identifier),
    };
}

function relaid(desk: Desk, from: number, to: number): Desk {
    const pending = pendingAt(desk.draft, from);
    if (pending === null || pendingAt(desk.draft, to) !== null) {
        return desk;
    }
    const moved: Pending = { ...pending, cell: to };
    return {
        ...desk,
        draft: laidDown(takenBack(desk.draft, from), moved),
        lift: liftWithout(desk.lift, pending.tile.identifier),
    };
}

function takenBackFrom(desk: Desk, cell: number): Desk {
    const pending = pendingAt(desk.draft, cell);
    if (pending === null) {
        return desk;
    }
    return {
        ...desk,
        draft: takenBack(desk.draft, cell),
        lift: liftWithout(desk.lift, pending.tile.identifier),
    };
}

function parked(desk: Desk, id: number, before: number | null): Desk {
    return {
        ...desk,
        tray: parkedTray(desk.tray, id, before),
        lift: liftWithout(desk.lift, id),
    };
}

function liftWithout(lift: Lift | null, id: number): Lift | null {
    if (lift !== null && lift.tile.identifier === id) {
        return null;
    }
    return lift;
}

function liftStillHeld(lift: Lift | null, rack: readonly Tile[] | null, committed: ReadonlySet<number>): boolean {
    if (lift === null) {
        return true;
    }
    if (rack === null || committed.has(lift.tile.identifier)) {
        return false;
    }
    return rack.some((tile) => tile.identifier === lift.tile.identifier);
}
