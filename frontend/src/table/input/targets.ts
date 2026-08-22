import type { Landing, RowRegion } from "../../play/board/landing";

export interface Rect {
    readonly left: number;
    readonly top: number;
    readonly width: number;
    readonly height: number;
}

export interface SlotRect {
    readonly id: number;
    readonly rect: Rect;
}

export interface RowTarget {
    readonly region: RowRegion;
    readonly rect: Rect;
    readonly slots: readonly SlotRect[];
}

export interface TargetMap {
    readonly size: number;
    readonly board: Rect | null;
    readonly viewport: Rect | null;
    readonly rows: readonly RowTarget[];
}

const ROW_REGIONS: readonly RowRegion[] = ["rack", "tray"];
const ROW_REACH_SHARE = 0.25;
const HALF_DIVISOR = 2;

export function targetsFrom(root: HTMLElement, size: number): TargetMap {
    return {
        size,
        board: regionRect(root, "board"),
        viewport: regionRect(root, "board-view"),
        rows: rowsFrom(root),
    };
}

export function rowsFrom(root: HTMLElement): readonly RowTarget[] {
    const rows: RowTarget[] = [];
    for (const region of ROW_REGIONS) {
        const rect = regionRect(root, region);
        if (rect !== null) {
            rows.push({ region, rect, slots: slotRects(root, region) });
        }
    }
    return rows;
}

export function withRows(targets: TargetMap, rows: readonly RowTarget[]): TargetMap {
    return { ...targets, rows };
}

export function landingAt(targets: TargetMap, x: number, y: number): Landing | null {
    const board = seenBoard(targets, x, y);
    if (board !== null) {
        return { kind: "cell", cell: cellAt(board, targets.size, x, y) };
    }
    return rowLanding(targets.rows, x, y);
}

export function overBoard(targets: TargetMap, x: number, y: number): boolean {
    return seenBoard(targets, x, y) !== null;
}

function seenBoard(targets: TargetMap, x: number, y: number): Rect | null {
    const inViewport = targets.viewport === null || within(targets.viewport, x, y);
    if (targets.board === null || !inViewport || !within(targets.board, x, y)) {
        return null;
    }
    return targets.board;
}

function regionRect(root: HTMLElement, region: string): Rect | null {
    const found = root.querySelector(`[data-region="${region}"]`);
    if (!(found instanceof HTMLElement)) {
        return null;
    }
    return plain(found.getBoundingClientRect());
}

function slotRects(root: HTMLElement, region: string): readonly SlotRect[] {
    const slots: SlotRect[] = [];
    for (const found of root.querySelectorAll(`[data-region="${region}"] [data-tile]`)) {
        if (!(found instanceof HTMLElement)) {
            continue;
        }
        const id = Number(found.dataset.tile);
        if (Number.isInteger(id)) {
            slots.push({ id, rect: plain(found.getBoundingClientRect()) });
        }
    }
    return slots;
}

function plain(rect: DOMRect): Rect {
    return { left: rect.left, top: rect.top, width: rect.width, height: rect.height };
}

function within(rect: Rect, x: number, y: number): boolean {
    return x >= rect.left && x < rect.left + rect.width && y >= rect.top && y < rect.top + rect.height;
}

function cellAt(board: Rect, size: number, x: number, y: number): number {
    const column = clamped(Math.floor(((x - board.left) / board.width) * size), size);
    const row = clamped(Math.floor(((y - board.top) / board.height) * size), size);
    return row * size + column;
}

function clamped(coordinate: number, size: number): number {
    return Math.min(Math.max(coordinate, 0), size - 1);
}

interface SlotBand {
    readonly rect: Rect;
    readonly slots: SlotRect[];
}

function rowLanding(rows: readonly RowTarget[], x: number, y: number): Landing | null {
    const row = nearest(rows, (candidate) => reachedBy(candidate.rect, x, y));
    if (row === null) {
        return null;
    }
    return { kind: row.region, before: gapIn(row.slots, x, y) };
}

function gapIn(slots: readonly SlotRect[], x: number, y: number): number | null {
    const band = nearest(bandsOf(slots), (candidate) => spanDistance(candidate.rect, y));
    const beyond = band?.slots.find((slot) => x < slot.rect.left + slot.rect.width / HALF_DIVISOR);
    return beyond?.id ?? null;
}

function bandsOf(slots: readonly SlotRect[]): readonly SlotBand[] {
    const bands: SlotBand[] = [];
    for (const slot of slots) {
        const current = bands.at(-1);
        if (current !== undefined && sameBand(current.rect, slot.rect)) {
            current.slots.push(slot);
            continue;
        }
        bands.push({ rect: slot.rect, slots: [slot] });
    }
    return bands;
}

function sameBand(band: Rect, slot: Rect): boolean {
    return Math.abs(slot.top - band.top) < band.height / HALF_DIVISOR;
}

function reachedBy(rect: Rect, x: number, y: number): number | null {
    if (x < rect.left || x >= rect.left + rect.width) {
        return null;
    }
    const distance = spanDistance(rect, y);
    return distance <= rect.height * ROW_REACH_SHARE ? distance : null;
}

function spanDistance(rect: Rect, y: number): number {
    return Math.max(rect.top - y, y - (rect.top + rect.height), 0);
}

function nearest<Item>(items: readonly Item[], distance: (item: Item) => number | null): Item | null {
    let found: Item | null = null;
    let shortest = Number.POSITIVE_INFINITY;
    for (const item of items) {
        const reach = distance(item);
        if (reach !== null && reach < shortest) {
            found = item;
            shortest = reach;
        }
    }
    return found;
}
