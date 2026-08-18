import type { Landing } from "../../play/board/landing";

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

export interface TargetMap {
    readonly size: number;
    readonly board: Rect | null;
    readonly rack: Rect | null;
    readonly rackSlots: readonly SlotRect[];
    readonly tray: Rect | null;
    readonly traySlots: readonly SlotRect[];
}

export function targetsFrom(root: HTMLElement, size: number): TargetMap {
    return {
        size,
        board: regionRect(root, "board"),
        rack: regionRect(root, "rack"),
        rackSlots: slotRects(root, "rack"),
        tray: regionRect(root, "tray"),
        traySlots: slotRects(root, "tray"),
    };
}

export function landingAt(targets: TargetMap, x: number, y: number): Landing | null {
    if (targets.board !== null && within(targets.board, x, y)) {
        return { kind: "cell", cell: cellAt(targets.board, targets.size, x, y) };
    }
    if (targets.rack !== null && within(targets.rack, x, y)) {
        return { kind: "rack", before: slotBefore(targets.rackSlots, x, y) };
    }
    if (targets.tray !== null && within(targets.tray, x, y)) {
        return { kind: "tray", before: slotBefore(targets.traySlots, x, y) };
    }
    return null;
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

const HALF_DIVISOR = 2;

function slotBefore(slots: readonly SlotRect[], x: number, y: number): number | null {
    for (const slot of slots) {
        const centerX = slot.rect.left + slot.rect.width / HALF_DIVISOR;
        const rowBottom = slot.rect.top + slot.rect.height;
        if (y < slot.rect.top) {
            return slot.id;
        }
        if (y < rowBottom && x < centerX) {
            return slot.id;
        }
    }
    return null;
}
