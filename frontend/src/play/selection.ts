import type { Tile } from "../api/views";
import type { DeskSpot } from "./spot";

export interface Lift {
    readonly tile: Tile;
    readonly from: DeskSpot;
}

export function toggledLift(lift: Lift | null, tile: Tile, from: DeskSpot): Lift | null {
    if (lift !== null && lift.tile.identifier === tile.identifier) {
        return null;
    }
    return { tile, from };
}

export function liftedIdentifier(lift: Lift | null): number | null {
    return lift === null ? null : lift.tile.identifier;
}
