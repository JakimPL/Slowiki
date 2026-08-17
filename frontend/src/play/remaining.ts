import type { TableDescription } from "../api/tables";
import type { Board, Tile } from "../api/views";

export interface RemainingLetter {
    readonly symbol: string;
    readonly category: string;
    readonly count: number;
}

export interface RemainingTally {
    readonly letters: readonly RemainingLetter[];
    readonly blanks: number;
}

export function remainingTally(
    description: TableDescription,
    board: Board,
    rack: readonly Tile[] | null,
): RemainingTally {
    const counts = new Map(
        description.alphabet.map((letter) => [letter.symbol, description.distribution[letter.symbol] ?? 0]),
    );
    let blanks = description.blanks;
    const spend = (tile: Tile): void => {
        if (tile.blank) {
            blanks -= 1;
            return;
        }
        counts.set(tile.letter, (counts.get(tile.letter) ?? 0) - 1);
    };
    for (const tile of board.tiles) {
        if (tile !== null) {
            spend(tile);
        }
    }
    for (const tile of rack ?? []) {
        spend(tile);
    }
    return {
        letters: description.alphabet.map((letter) => ({
            symbol: letter.symbol,
            category: letter.category,
            count: Math.max(0, counts.get(letter.symbol) ?? 0),
        })),
        blanks: Math.max(0, blanks),
    };
}
