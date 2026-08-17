import type { Tile } from "../api/views";

export interface Lift {
    readonly tile: Tile;
}

export function toggledLift(lift: Lift | null, tile: Tile): Lift | null {
    if (lift !== null && lift.tile.identifier === tile.identifier) {
        return null;
    }
    return { tile };
}

export function liftedIdentifier(lift: Lift | null): number | null {
    return lift === null ? null : lift.tile.identifier;
}
