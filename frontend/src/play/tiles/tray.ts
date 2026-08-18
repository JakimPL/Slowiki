import type { Tile } from "../../api/views";
import type { IdRow } from "./row";
import { insertedBefore, withoutId } from "./row";

export type Tray = IdRow;

export const EMPTY_TRAY: Tray = [];

export function parkedTray(tray: Tray, id: number, before: number | null): Tray {
    return insertedBefore(tray, id, before);
}

export function retrievedTray(tray: Tray, id: number): Tray {
    return withoutId(tray, id);
}

export function reconciledTray(tray: Tray, rack: readonly Tile[] | null): Tray {
    if (rack === null) {
        return tray.length === 0 ? tray : EMPTY_TRAY;
    }
    const held = new Set(rack.map((tile) => tile.identifier));
    const kept = tray.filter((id) => held.has(id));
    return kept.length === tray.length ? tray : kept;
}

export function trayTilesOf(tray: Tray, rack: readonly Tile[]): readonly Tile[] {
    const byId = new Map(rack.map((tile) => [tile.identifier, tile]));
    return tray.map((id) => byId.get(id)).filter((tile) => tile !== undefined);
}
