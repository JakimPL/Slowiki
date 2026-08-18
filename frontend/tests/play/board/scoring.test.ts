import { describe, expect, it } from "vitest";

import type { Laid } from "../../../src/play/board/geometry";
import { formationOf } from "../../../src/play/board/geometry";
import { scoredWordsOf } from "../../../src/play/board/scoring";
import { aBoard, aTile } from "../../fixtures/positions";

const CENTER = 112;

function laid(cell: number, letter: string, value: number, identifier: number, category = "yellow"): Laid {
    return { cell, tile: aTile({ identifier, letter, value, category }) };
}

function scored(
    board: ReturnType<typeof aBoard>,
    pieces: readonly Laid[],
): readonly { text: string; points: number }[] {
    const formation = formationOf(board, pieces);
    expect(formation.verdict).toBe("playable");
    return scoredWordsOf(board, pieces, formation.words);
}

describe("scoredWordsOf", () => {
    it("sums plain letter values", () => {
        const words = scored(aBoard(), [laid(CENTER, "K", 2, 1), laid(CENTER + 1, "O", 3, 2)]);
        expect(words).toEqual([{ text: "KO", points: 5 }]);
    });

    it("multiplies a fresh letter on a letter premium", () => {
        const board = aBoard({}, { [CENTER + 1]: { kind: "letter_multiplier", multiplier: 3, category: null } });
        const words = scored(board, [laid(CENTER, "K", 2, 1), laid(CENTER + 1, "O", 3, 2)]);
        expect(words).toEqual([{ text: "KO", points: 11 }]);
    });

    it("multiplies the whole word on a fresh word premium", () => {
        const board = aBoard({}, { [CENTER]: { kind: "word_multiplier", multiplier: 2, category: null } });
        const words = scored(board, [laid(CENTER, "K", 2, 1), laid(CENTER + 1, "O", 3, 2)]);
        expect(words).toEqual([{ text: "KO", points: 10 }]);
    });

    it("honors a category premium only for matching tiles", () => {
        const board = aBoard(
            {},
            {
                [CENTER]: { kind: "category_multiplier", multiplier: 3, category: "yellow" },
                [CENTER + 1]: { kind: "category_multiplier", multiplier: 3, category: "red" },
            },
        );
        const words = scored(board, [laid(CENTER, "K", 2, 1), laid(CENTER + 1, "O", 3, 2)]);
        expect(words).toEqual([{ text: "KO", points: 9 }]);
    });

    it("leaves premiums under existing tiles spent", () => {
        const board = aBoard(
            { [CENTER]: aTile({ letter: "A", value: 4 }) },
            { [CENTER]: { kind: "word_multiplier", multiplier: 3, category: null } },
        );
        const words = scored(board, [laid(CENTER + 1, "B", 2, 2)]);
        expect(words).toEqual([{ text: "AB", points: 6 }]);
    });

    it("scores an assigned blank as zero", () => {
        const blank: Laid = {
            cell: CENTER + 1,
            tile: aTile({ identifier: 2, letter: "Ż", value: 0, category: "blank", blank: true }),
        };
        const board = aBoard({}, { [CENTER + 1]: { kind: "category_multiplier", multiplier: 3, category: "red" } });
        const words = scored(board, [laid(CENTER, "K", 2, 1), blank]);
        expect(words).toEqual([{ text: "KŻ", points: 2 }]);
    });

    it("counts a shared fresh tile with its premium in both words", () => {
        const board = aBoard(
            {
                [CENTER]: aTile({ letter: "A", value: 1 }),
                [CENTER + 15]: aTile({ letter: "B", value: 1, identifier: 2 }),
            },
            { [CENTER + 16]: { kind: "letter_multiplier", multiplier: 2, category: null } },
        );
        const pieces = [laid(CENTER + 1, "C", 3, 3), laid(CENTER + 16, "D", 5, 4)];
        const words = scored(board, pieces);
        expect(words).toEqual([
            { text: "CD", points: 13 },
            { text: "AC", points: 4 },
            { text: "BD", points: 11 },
        ]);
    });
});
