import type { Move, PlayPlacement } from "../api/moves";
import type { PositionView, Tile } from "../api/views";
import { cellIndex } from "./board";
import type { LogEntry } from "./log";

export type PremoveKind = "play" | "exchange";

export interface PremoveGhost {
    readonly cell: number;
    readonly tile: Tile;
}

export interface QueuedPremove {
    readonly kind: PremoveKind;
    readonly ghosts: readonly PremoveGhost[];
    readonly committed: ReadonlySet<number>;
}

export const NO_COMMITTED_TILES: ReadonlySet<number> = new Set();

export function queuedPremoveOf(view: PositionView, mySeat: number | null): QueuedPremove | null {
    const move = view.premove;
    if (move === null || mySeat === null || move.player !== mySeat) {
        return null;
    }
    return mirroredAction(move, view, mySeat);
}

export function returnedPremoveOf(log: readonly LogEntry[], mySeat: number | null): LogEntry | null {
    if (mySeat === null) {
        return null;
    }
    for (let index = log.length - 1; index >= 0; index -= 1) {
        const entry = log[index];
        if (entry?.kind === "premove-returned" && entry.actor === mySeat) {
            return entry;
        }
    }
    return null;
}

function mirroredAction(move: Move, view: PositionView, mySeat: number): QueuedPremove | null {
    const action = move.action;
    if (action.kind === "play") {
        const rack = view.racks[String(mySeat)] ?? [];
        return {
            kind: "play",
            ghosts: ghostsOf(action.placements, rack, view.board.size),
            committed: new Set(action.placements.map((placement) => placement.tile_id)),
        };
    }
    if (action.kind === "exchange") {
        return { kind: "exchange", ghosts: [], committed: new Set(action.tile_ids) };
    }
    return null;
}

function ghostsOf(placements: readonly PlayPlacement[], rack: readonly Tile[], size: number): readonly PremoveGhost[] {
    const held = new Map(rack.map((tile) => [tile.identifier, tile]));
    const ghosts: PremoveGhost[] = [];
    for (const placement of placements) {
        const tile = held.get(placement.tile_id);
        if (tile !== undefined) {
            ghosts.push({
                cell: cellIndex(size, placement.row, placement.column),
                tile: faced(tile, placement.letter ?? null),
            });
        }
    }
    return ghosts;
}

function faced(tile: Tile, letter: string | null): Tile {
    if (letter === null) {
        return tile;
    }
    return { ...tile, letter };
}
