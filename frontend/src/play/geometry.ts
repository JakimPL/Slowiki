import type { Board, Tile } from "../api/views";
import { boardIsEmpty, cellIndex, centerIndex, columnOf, combinedTiles, rowOf, tileAt } from "./board";

export interface Laid {
    readonly cell: number;
    readonly tile: Tile;
}

export type GeometryVerdict =
    | "empty"
    | "opening-short"
    | "off-center"
    | "detached"
    | "scattered"
    | "gapped"
    | "playable";

export interface FormedWord {
    readonly cells: readonly number[];
    readonly text: string;
}

export interface Formation {
    readonly verdict: GeometryVerdict;
    readonly words: readonly FormedWord[];
}

const OPENING_MINIMUM = 2;
const NEIGHBORS: readonly (readonly [number, number])[] = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1],
];

export function formationOf(board: Board, laid: readonly Laid[]): Formation {
    if (laid.length === 0) {
        return { verdict: "empty", words: [] };
    }
    const anchor = anchorVerdict(board, laid);
    if (anchor !== null) {
        return { verdict: anchor, words: [] };
    }
    const combined = combinedTiles(board, new Map(laid.map((piece) => [piece.cell, piece.tile])));
    return formedOnLines(combined, board.size, laid);
}

function anchorVerdict(board: Board, laid: readonly Laid[]): GeometryVerdict | null {
    if (boardIsEmpty(board)) {
        if (laid.length < OPENING_MINIMUM) {
            return "opening-short";
        }
        return laid.some((piece) => piece.cell === centerIndex(board.size)) ? null : "off-center";
    }
    return laid.some((piece) => touchesExisting(board, piece.cell)) ? null : "detached";
}

function touchesExisting(board: Board, cell: number): boolean {
    const row = rowOf(board.size, cell);
    const column = columnOf(board.size, cell);
    return NEIGHBORS.some(([rowStep, columnStep]) => {
        const neighborRow = row + rowStep;
        const neighborColumn = column + columnStep;
        if (neighborRow < 0 || neighborRow >= board.size || neighborColumn < 0 || neighborColumn >= board.size) {
            return false;
        }
        return tileAt(board, cellIndex(board.size, neighborRow, neighborColumn)) !== null;
    });
}

function formedOnLines(combined: readonly (Tile | null)[], size: number, laid: readonly Laid[]): Formation {
    const first = laid[0];
    if (first === undefined) {
        return { verdict: "empty", words: [] };
    }
    if (laid.length === 1) {
        return singleTileFormation(combined, size, first);
    }
    const rows = new Set(laid.map((piece) => rowOf(size, piece.cell)));
    const columns = new Set(laid.map((piece) => columnOf(size, piece.cell)));
    if (rows.size === 1) {
        return axisFormation(combined, size, laid, rowOf(size, first.cell), true);
    }
    if (columns.size === 1) {
        return axisFormation(combined, size, laid, columnOf(size, first.cell), false);
    }
    return { verdict: "scattered", words: [] };
}

function singleTileFormation(combined: readonly (Tile | null)[], size: number, piece: Laid): Formation {
    const row = rowOf(size, piece.cell);
    const column = columnOf(size, piece.cell);
    const across = lineWord(combined, size, row, column, true);
    const down = lineWord(combined, size, column, row, false);
    const words = [across, down].filter((word) => word !== null);
    return { verdict: "playable", words };
}

function axisFormation(
    combined: readonly (Tile | null)[],
    size: number,
    laid: readonly Laid[],
    fixed: number,
    horizontal: boolean,
): Formation {
    const positions = laid.map((piece) =>
        horizontal ? columnOf(size, piece.cell) : rowOf(size, piece.cell),
    );
    const low = Math.min(...positions);
    const high = Math.max(...positions);
    for (let coordinate = low; coordinate <= high; coordinate += 1) {
        if (tileOnLine(combined, size, fixed, coordinate, horizontal) === null) {
            return { verdict: "gapped", words: [] };
        }
    }
    const span = lineSpan(combined, size, fixed, low, high, horizontal);
    const main = wordOnSpan(combined, size, fixed, span, horizontal);
    return { verdict: "playable", words: [main, ...crossWords(combined, size, laid, horizontal)] };
}

function crossWords(
    combined: readonly (Tile | null)[],
    size: number,
    laid: readonly Laid[],
    horizontal: boolean,
): readonly FormedWord[] {
    const words: FormedWord[] = [];
    for (const piece of laid) {
        const row = rowOf(size, piece.cell);
        const column = columnOf(size, piece.cell);
        const cross = horizontal
            ? lineWord(combined, size, column, row, false)
            : lineWord(combined, size, row, column, true);
        if (cross !== null && !words.some((word) => sameWord(word, cross))) {
            words.push(cross);
        }
    }
    return words;
}

function sameWord(left: FormedWord, right: FormedWord): boolean {
    return left.text === right.text && left.cells[0] === right.cells[0];
}

function lineWord(
    combined: readonly (Tile | null)[],
    size: number,
    fixed: number,
    at: number,
    horizontal: boolean,
): FormedWord | null {
    const [start, end] = lineSpan(combined, size, fixed, at, at, horizontal);
    if (start === end) {
        return null;
    }
    return wordOnSpan(combined, size, fixed, [start, end], horizontal);
}

function lineSpan(
    combined: readonly (Tile | null)[],
    size: number,
    fixed: number,
    low: number,
    high: number,
    horizontal: boolean,
): readonly [number, number] {
    let start = low;
    while (start > 0 && tileOnLine(combined, size, fixed, start - 1, horizontal) !== null) {
        start -= 1;
    }
    let end = high;
    while (end < size - 1 && tileOnLine(combined, size, fixed, end + 1, horizontal) !== null) {
        end += 1;
    }
    return [start, end];
}

function wordOnSpan(
    combined: readonly (Tile | null)[],
    size: number,
    fixed: number,
    span: readonly [number, number],
    horizontal: boolean,
): FormedWord {
    const [start, end] = span;
    const cells: number[] = [];
    let text = "";
    for (let coordinate = start; coordinate <= end; coordinate += 1) {
        const cell = cellOnLine(size, fixed, coordinate, horizontal);
        cells.push(cell);
        text += combined[cell]?.letter ?? "";
    }
    return { cells, text };
}

function cellOnLine(size: number, fixed: number, coordinate: number, horizontal: boolean): number {
    return horizontal ? cellIndex(size, fixed, coordinate) : cellIndex(size, coordinate, fixed);
}

function tileOnLine(
    combined: readonly (Tile | null)[],
    size: number,
    fixed: number,
    coordinate: number,
    horizontal: boolean,
): Tile | null {
    return combined[cellOnLine(size, fixed, coordinate, horizontal)] ?? null;
}
