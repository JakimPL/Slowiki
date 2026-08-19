import { describe, expect, it } from "vitest";

import { cellIndex } from "../../../src/play/board/board";
import { standingWordsAt } from "../../../src/play/board/standing";
import { aBoard, aTile } from "../../fixtures/positions";

const SIZE = 15;
const ROW = 7;
const COLUMN = 7;

function placed(
    letters: string,
    row: number,
    column: number,
    horizontal: boolean,
): Record<number, ReturnType<typeof aTile>> {
    const tiles: Record<number, ReturnType<typeof aTile>> = {};
    Array.from(letters).forEach((letter, step) => {
        const cell = horizontal ? cellIndex(SIZE, row, column + step) : cellIndex(SIZE, row + step, column);
        tiles[cell] = aTile({ identifier: cell, letter });
    });
    return tiles;
}

describe("standingWordsAt", () => {
    it("reads the word running across the square", () => {
        const board = aBoard(placed("KOT", ROW, COLUMN, true));
        expect(standingWordsAt(board, cellIndex(SIZE, ROW, COLUMN + 1))).toStrictEqual([
            {
                cells: [
                    cellIndex(SIZE, ROW, COLUMN),
                    cellIndex(SIZE, ROW, COLUMN + 1),
                    cellIndex(SIZE, ROW, COLUMN + 2),
                ],
                text: "KOT",
            },
        ]);
    });

    it("reads the word running down the square", () => {
        const board = aBoard(placed("KOT", ROW, COLUMN, false));
        expect(standingWordsAt(board, cellIndex(SIZE, ROW + 2, COLUMN)).map((word) => word.text)).toStrictEqual([
            "KOT",
        ]);
    });

    it("reads both words where two cross, across before down", () => {
        const board = aBoard({ ...placed("KOT", ROW, COLUMN, true), ...placed("OSA", ROW, COLUMN + 1, false) });
        const words = standingWordsAt(board, cellIndex(SIZE, ROW, COLUMN + 1));
        expect(words.map((word) => word.text)).toStrictEqual(["KOT", "OSA"]);
    });

    it("answers nothing for an empty square", () => {
        const board = aBoard(placed("KOT", ROW, COLUMN, true));
        expect(standingWordsAt(board, cellIndex(SIZE, ROW + 4, COLUMN))).toStrictEqual([]);
    });

    it("answers nothing for a tile no word runs through", () => {
        const board = aBoard(placed("K", ROW, COLUMN, true));
        expect(standingWordsAt(board, cellIndex(SIZE, ROW, COLUMN))).toStrictEqual([]);
    });

    it("prints the letter a blank carries", () => {
        const board = aBoard({
            [cellIndex(SIZE, ROW, COLUMN)]: aTile({ identifier: 1, letter: "K" }),
            [cellIndex(SIZE, ROW, COLUMN + 1)]: aTile({ identifier: 2, letter: "O", blank: true, value: 0 }),
        });
        expect(standingWordsAt(board, cellIndex(SIZE, ROW, COLUMN)).map((word) => word.text)).toStrictEqual(["KO"]);
    });
});
