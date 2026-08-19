import { describe, expect, it } from "vitest";

import type { WordHighlight } from "../../../src/api/highlights";
import { highlightRows } from "../../../src/play/story/highlights";

const BEST: WordHighlight = { player: 1, word: "KOTLETY", points: 30, turn_number: 6 };

const LONGEST: WordHighlight = { player: 0, word: "PODESZWA", points: 18, turn_number: 3 };

describe("highlightRows", () => {
    it("names the best word and the longest word apart", () => {
        const rows = highlightRows({ best_word: BEST, longest_word: LONGEST });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
        expect(rows[0]?.word).toBe("KOTLETY");
        expect(rows[0]?.points).toBe(30);
        expect(rows[1]?.word).toBe("PODESZWA");
        expect(rows[1]?.points).toBe(18);
        expect(rows[1]?.player).toBe(0);
    });

    it("folds one word that was both into a single row", () => {
        const rows = highlightRows({ best_word: BEST, longest_word: BEST });
        expect(rows.map((row) => row.kind)).toEqual(["both"]);
        expect(rows[0]?.word).toBe("KOTLETY");
        expect(rows[0]?.points).toBe(30);
    });

    it("keeps both rows when the same word was laid again on another turn", () => {
        const rows = highlightRows({ best_word: BEST, longest_word: { ...BEST, turn_number: 2 } });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
    });

    it("keeps both rows when one play spelled both words at once", () => {
        const rows = highlightRows({ best_word: BEST, longest_word: { ...LONGEST, player: 1, turn_number: 6 } });
        expect(rows.map((row) => row.kind)).toEqual(["best", "longest"]);
    });

    it("leaves the room empty when a game was played out in passes", () => {
        expect(highlightRows({ best_word: null, longest_word: null })).toEqual([]);
    });
});
