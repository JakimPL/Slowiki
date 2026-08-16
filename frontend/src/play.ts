import type { MovePayload, PlacementPayload } from "./api";

export function playMove(player: number, placements: PlacementPayload[]): MovePayload {
    return { player, action: { kind: "play", placements } };
}

export function exchangeMove(player: number, tileIds: number[]): MovePayload {
    return { player, action: { kind: "exchange", tile_ids: tileIds } };
}

export function passMove(player: number): MovePayload {
    return { player, action: { kind: "pass" } };
}
