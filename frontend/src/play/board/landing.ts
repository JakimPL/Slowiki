import type { Tile } from "../../api/views";

export type RowRegion = "rack" | "tray";

export type Landing =
    | { readonly kind: "cell"; readonly cell: number }
    | { readonly kind: "rack"; readonly before: number | null }
    | { readonly kind: "tray"; readonly before: number | null };

export interface Incoming {
    readonly carried: number;
    readonly before: number | null;
}

export interface LandedRow {
    readonly tiles: readonly Tile[];
    readonly shadowAt: number | null;
}

export function incomingOf(landing: Landing | null, carried: number, region: RowRegion): Incoming | null {
    if (landing === null || landing.kind === "cell" || landing.kind !== region) {
        return null;
    }
    return { carried, before: landing.before };
}

export function landedRow(tiles: readonly Tile[], incoming: Incoming | null): LandedRow {
    if (incoming === null) {
        return { tiles, shadowAt: null };
    }
    const resting = tiles.filter((tile) => tile.identifier !== incoming.carried);
    const at = incoming.before === null ? -1 : resting.findIndex((tile) => tile.identifier === incoming.before);
    return { tiles: resting, shadowAt: at === -1 ? resting.length : at };
}
