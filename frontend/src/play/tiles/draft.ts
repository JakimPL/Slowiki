import type { PlayPlacement } from "../../api/moves";
import type { Board, Tile } from "../../api/views";
import { columnOf, rowOf, tileAt } from "../board/board";
import type { Laid } from "../board/geometry";

export interface Pending {
    readonly cell: number;
    readonly tile: Tile;
    readonly letter: string | null;
}

export type Draft = readonly Pending[];

export const EMPTY_DRAFT: Draft = [];

export function pendingAt(draft: Draft, cell: number): Pending | null {
    return draft.find((pending) => pending.cell === cell) ?? null;
}

export function laidDown(draft: Draft, pending: Pending): Draft {
    if (pendingAt(draft, pending.cell) !== null) {
        return draft;
    }
    return [...draft, pending];
}

export function relaidDraft(draft: Draft, from: number, to: number): Draft {
    return draft.map((pending) => movedPending(pending, from, to));
}

function movedPending(pending: Pending, from: number, to: number): Pending {
    if (pending.cell === from) {
        return { ...pending, cell: to };
    }
    if (pending.cell === to) {
        return { ...pending, cell: from };
    }
    return pending;
}

export function takenBack(draft: Draft, cell: number): Draft {
    return draft.filter((pending) => pending.cell !== cell);
}

export function stamped(draft: Draft, cell: number, letter: string): Draft {
    return draft.map((pending) => (pending.cell === cell ? { ...pending, letter } : pending));
}

export function draftedIdentifiers(draft: Draft): ReadonlySet<number> {
    return new Set(draft.map((pending) => pending.tile.identifier));
}

export function shownTile(pending: Pending): Tile {
    if (pending.letter === null) {
        return pending.tile;
    }
    return { ...pending.tile, letter: pending.letter };
}

export function laidOf(draft: Draft): readonly Laid[] {
    return draft.map((pending) => ({ cell: pending.cell, tile: shownTile(pending) }));
}

export function placementsOf(draft: Draft, size: number): PlayPlacement[] {
    return draft.map((pending) => ({
        tile_id: pending.tile.identifier,
        row: rowOf(size, pending.cell),
        column: columnOf(size, pending.cell),
        letter: pending.letter,
    }));
}

export function reconciledDraft(
    draft: Draft,
    rack: readonly Tile[] | null,
    board: Board,
    committed: ReadonlySet<number>,
): Draft {
    if (rack === null) {
        return draft.length === 0 ? draft : EMPTY_DRAFT;
    }
    const held = new Set(rack.map((tile) => tile.identifier));
    const kept = draft.filter(
        (pending) =>
            held.has(pending.tile.identifier) &&
            !committed.has(pending.tile.identifier) &&
            tileAt(board, pending.cell) === null,
    );
    return kept.length === draft.length ? draft : kept;
}
