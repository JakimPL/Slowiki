import type { Schemas } from "./views";

export type Move = Schemas["Move"];
export type PlayPlacement = Schemas["PlayPlacement"];
export type MoveRequest = Schemas["MoveRequest"];
export type MoveAccepted = Schemas["MoveAccepted"];

export function playMove(player: number, placements: readonly PlayPlacement[]): Move {
    return { player, action: { kind: "play", placements: [...placements] } };
}

export function exchangeMove(player: number, tileIdentifiers: readonly number[]): Move {
    return { player, action: { kind: "exchange", tile_ids: [...tileIdentifiers] } };
}

export function passMove(player: number): Move {
    return { player, action: { kind: "pass" } };
}

export function reorderMove(player: number, tileIdentifiers: readonly number[]): Move {
    return { player, action: { kind: "reorder", tile_ids: [...tileIdentifiers] } };
}
