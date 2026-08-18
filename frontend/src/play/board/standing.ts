import type { Board } from "../../api/views";
import { tileAt } from "./board";
import type { FormedWord } from "./geometry";
import { wordsThroughCell } from "./geometry";

export function standingWordsAt(board: Board, cell: number): readonly FormedWord[] {
    if (tileAt(board, cell) === null) {
        return [];
    }
    return wordsThroughCell(board.tiles, board.size, cell);
}
