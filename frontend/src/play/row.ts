export type IdRow = readonly number[];

export function insertedBefore(row: IdRow, id: number, before: number | null): IdRow {
    const cleared = row.filter((present) => present !== id);
    if (before === null) {
        return [...cleared, id];
    }
    const at = cleared.indexOf(before);
    if (at === -1) {
        return [...cleared, id];
    }
    return [...cleared.slice(0, at), id, ...cleared.slice(at)];
}

export function withoutId(row: IdRow, id: number): IdRow {
    return row.filter((present) => present !== id);
}
