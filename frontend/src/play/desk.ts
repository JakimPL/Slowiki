import type { Board, Tile } from "../api/views";
import type { Draft } from "./draft";
import { EMPTY_DRAFT, laidDown, pendingAt, reconciledDraft, takenBack } from "./draft";
import type { Lift } from "./selection";
import { toggledLift } from "./selection";

export interface Desk {
    readonly draft: Draft;
    readonly lift: Lift | null;
}

export const EMPTY_DESK: Desk = { draft: EMPTY_DRAFT, lift: null };

export type DeskEffect =
    | { readonly kind: "lift"; readonly tile: Tile }
    | { readonly kind: "lay"; readonly cell: number; readonly letter: string | null }
    | { readonly kind: "take-back"; readonly cell: number }
    | { readonly kind: "recall" }
    | { readonly kind: "clear-lift" };

export function affected(desk: Desk, effect: DeskEffect): Desk {
    switch (effect.kind) {
        case "lift":
            return { ...desk, lift: toggledLift(desk.lift, effect.tile) };
        case "lay":
            return laid(desk, effect.cell, effect.letter);
        case "take-back":
            return { ...desk, draft: takenBack(desk.draft, effect.cell) };
        case "recall":
            return EMPTY_DESK;
        case "clear-lift":
            return { ...desk, lift: null };
    }
}

export function reconciledDesk(desk: Desk, rack: readonly Tile[] | null, board: Board): Desk {
    const draft = reconciledDraft(desk.draft, rack, board);
    const lift = liftStillHeld(desk.lift, rack) ? desk.lift : null;
    if (draft === desk.draft && lift === desk.lift) {
        return desk;
    }
    return { draft, lift };
}

function laid(desk: Desk, cell: number, letter: string | null): Desk {
    if (desk.lift === null || pendingAt(desk.draft, cell) !== null) {
        return desk;
    }
    return {
        draft: laidDown(desk.draft, { cell, tile: desk.lift.tile, letter }),
        lift: null,
    };
}

function liftStillHeld(lift: Lift | null, rack: readonly Tile[] | null): boolean {
    if (lift === null) {
        return true;
    }
    if (rack === null) {
        return false;
    }
    return rack.some((tile) => tile.identifier === lift.tile.identifier);
}
