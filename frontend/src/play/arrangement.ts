import type { Tile } from "../api/views";
import type { IdRow } from "./row";
import { insertedBefore } from "./row";

export type Arrangement = IdRow;

export const EMPTY_ARRANGEMENT: Arrangement = [];

export function reconciledArrangement(arrangement: Arrangement, rack: readonly Tile[] | null): Arrangement {
    if (rack === null) {
        return arrangement.length === 0 ? arrangement : EMPTY_ARRANGEMENT;
    }
    const served = rack.map((tile) => tile.identifier);
    if (sameMembers(arrangement, served)) {
        return arrangement;
    }
    return served;
}

export function movedBefore(arrangement: Arrangement, id: number, before: number | null): Arrangement {
    if (!arrangement.includes(id)) {
        return arrangement;
    }
    return insertedBefore(arrangement, id, before);
}

export function shuffledArrangement(
    arrangement: Arrangement,
    visible: ReadonlySet<number>,
    random: () => number,
): Arrangement {
    const shuffled = [...arrangement.filter((id) => visible.has(id))];
    for (let slot = shuffled.length - 1; slot > 0; slot -= 1) {
        const swap = Math.floor(random() * (slot + 1));
        const kept = shuffled[slot];
        const chosen = shuffled[swap];
        if (kept !== undefined && chosen !== undefined) {
            shuffled[slot] = chosen;
            shuffled[swap] = kept;
        }
    }
    let cursor = 0;
    return arrangement.map((id) => {
        if (!visible.has(id)) {
            return id;
        }
        const next = shuffled[cursor];
        cursor += 1;
        return next ?? id;
    });
}

export function arrangedTiles(arrangement: Arrangement, rack: readonly Tile[]): readonly Tile[] {
    const byId = new Map(rack.map((tile) => [tile.identifier, tile]));
    return arrangement.map((id) => byId.get(id)).filter((tile) => tile !== undefined);
}

export function reorderPayload(arrangement: Arrangement, tray: IdRow, drafted: ReadonlySet<number>): readonly number[] {
    const parked = new Set(tray);
    const rackRow = arrangement.filter((id) => !parked.has(id) && !drafted.has(id));
    const draftedRow = arrangement.filter((id) => drafted.has(id));
    return [...rackRow, ...tray, ...draftedRow];
}

function sameMembers(left: IdRow, right: IdRow): boolean {
    if (left.length !== right.length) {
        return false;
    }
    const sortedLeft = [...left].sort((first, second) => first - second);
    const sortedRight = [...right].sort((first, second) => first - second);
    return sortedLeft.every((id, at) => id === sortedRight[at]);
}
