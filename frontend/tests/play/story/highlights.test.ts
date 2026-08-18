import { describe, expect, it } from "vitest";

import type { GameHighlights } from "../../../src/api/highlights";
import { highlightRows } from "../../../src/play/story/highlights";

const BEST: NonNullable<GameHighlights["best_play"]> = {
    player: 1,
    words: [
        { text: "KOTLETY", points: 30 },
        { text: "OS", points: 4 },
    ],
    points: 84,
    turn_number: 6,
};

const LONGEST: NonNullable<GameHighlights["longest_word"]> = {
    player: 0,
    word: "PODESZWA",
    points: 18,
    turn_number: 3,
};

describe("highlightRows", () => {
    it("names the best move and the longest word apart", () => {
        const rows = highlightRows({ best_play: BEST, longest_word: LONGEST });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
        expect(rows[0]?.points).toBe(84);
        expect(rows[1]?.words.map((word) => word.text)).toEqual(["PODESZWA"]);
        expect(rows[1]?.points).toBe(18);
        expect(rows[1]?.player).toBe(0);
    });

    it("folds one play that was both into a single row carrying its full score", () => {
        const play = { player: 2, words: [{ text: "DLUBALO", points: 32 }], points: 82, turn_number: 4 };
        const rows = highlightRows({
            best_play: play,
            longest_word: { player: 2, word: "DLUBALO", points: 32, turn_number: 4 },
        });
        expect(rows.map((row) => row.kind)).toEqual(["both"]);
        expect(rows[0]?.points).toBe(82);
    });

    it("keeps both rows when the best play spelled more than the longest word", () => {
        const rows = highlightRows({
            best_play: BEST,
            longest_word: { player: 1, word: "KOTLETY", points: 30, turn_number: 6 },
        });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
    });

    it("keeps both rows when one player made the longest word on another turn", () => {
        const rows = highlightRows({
            best_play: BEST,
            longest_word: { player: 1, word: "PODESZWA", points: 18, turn_number: 2 },
        });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
    });

    it("leaves the room empty when a game was played out in passes", () => {
        expect(highlightRows({ best_play: null, longest_word: null })).toEqual([]);
    });
});
