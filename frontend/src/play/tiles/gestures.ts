import type { Tile } from "../../api/views";
import type { Landing, RowRegion } from "../board/landing";
import type { DeskSpot } from "../board/spot";
import type { DeskEffect } from "./desk";
import type { Lift } from "./selection";

export function tapEffects(lift: Lift | null, spot: DeskSpot, tile: Tile): readonly DeskEffect[] {
    if (lift === null) {
        return [{ kind: "lift", tile, from: spot }];
    }
    if (spot.kind === "cell") {
        return cellTapEffects(lift, spot.cell, tile);
    }
    if (lift.from.kind === spot.kind) {
        return [{ kind: "lift", tile, from: spot }];
    }
    return rowEffects(lift.from, lift.tile, spot.kind, tile.identifier);
}

export function dropEffects(
    spot: DeskSpot,
    tile: Tile,
    landing: Landing | null,
    mayAct: boolean,
): readonly DeskEffect[] {
    if (landing === null) {
        return homeEffects(spot, tile);
    }
    if (landing.kind === "cell") {
        return mayAct ? cellEffects(spot, tile, landing.cell) : [];
    }
    return rowEffects(spot, tile, landing.kind, landing.before);
}

export function blankLanding(spot: DeskSpot, tile: Tile, landing: Landing | null): number | null {
    if (landing?.kind !== "cell" || spot.kind === "cell" || !tile.blank) {
        return null;
    }
    return landing.cell;
}

function cellTapEffects(lift: Lift, cell: number, tile: Tile): readonly DeskEffect[] {
    if (lift.from.kind !== "cell" || lift.from.cell === cell) {
        return [{ kind: "lift", tile, from: { kind: "cell", cell } }];
    }
    return [{ kind: "relay", from: lift.from.cell, to: cell }];
}

function homeEffects(spot: DeskSpot, tile: Tile): readonly DeskEffect[] {
    switch (spot.kind) {
        case "rack":
            return [];
        case "tray":
            return [{ kind: "retrieve", id: tile.identifier, before: null }];
        case "cell":
            return [{ kind: "take-back", cell: spot.cell }];
    }
}

function cellEffects(spot: DeskSpot, tile: Tile, cell: number): readonly DeskEffect[] {
    if (spot.kind === "cell") {
        return spot.cell === cell ? [] : [{ kind: "relay", from: spot.cell, to: cell }];
    }
    return [{ kind: "lay", cell, tile, letter: null }];
}

function rowEffects(spot: DeskSpot, tile: Tile, region: RowRegion, before: number | null): readonly DeskEffect[] {
    const arrival = arrivalEffect(spot, tile.identifier, region, before);
    if (spot.kind === "cell") {
        return [{ kind: "take-back", cell: spot.cell }, arrival];
    }
    return [arrival];
}

function arrivalEffect(spot: DeskSpot, identifier: number, region: RowRegion, before: number | null): DeskEffect {
    if (region === "tray") {
        return { kind: "park", id: identifier, before };
    }
    if (spot.kind === "tray") {
        return { kind: "retrieve", id: identifier, before };
    }
    return { kind: "reorder", id: identifier, before };
}
