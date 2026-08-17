import type { Tile } from "../api/views";

export type LiftSource = "rack" | "tray";

export interface Lift {
    readonly tile: Tile;
    readonly from: LiftSource;
}

export function toggledLift(lift: Lift | null, tile: Tile, from: LiftSource): Lift | null {
    if (lift !== null && lift.tile.identifier === tile.identifier) {
        return null;
    }
    return { tile, from };
}

export function liftedIdentifier(lift: Lift | null): number | null {
    return lift === null ? null : lift.tile.identifier;
}
