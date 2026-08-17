import type { Board, Tile } from "../api/views";

const CENTER_DIVISOR = 2;

export function cellIndex(size: number, row: number, column: number): number {
    return row * size + column;
}

export function rowOf(size: number, cell: number): number {
    return Math.floor(cell / size);
}

export function columnOf(size: number, cell: number): number {
    return cell % size;
}

export function centerIndex(size: number): number {
    const middle = Math.floor(size / CENTER_DIVISOR);
    return cellIndex(size, middle, middle);
}

export function inBounds(size: number, row: number, column: number): boolean {
    return row >= 0 && row < size && column >= 0 && column < size;
}

export function boardIsEmpty(board: Board): boolean {
    return board.tiles.every((tile) => tile === null);
}

export function tileAt(board: Board, cell: number): Tile | null {
    return board.tiles[cell] ?? null;
}

export function combinedTiles(board: Board, pending: ReadonlyMap<number, Tile>): readonly (Tile | null)[] {
    return board.tiles.map((tile, cell) => tile ?? pending.get(cell) ?? null);
}
