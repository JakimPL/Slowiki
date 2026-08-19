import type { Board } from "../../api/views";
import type { TableRules } from "../live/rules";
import type { Draft } from "../tiles/draft";
import { laidOf } from "../tiles/draft";
import type { GeometryVerdict } from "./geometry";
import { formationOf } from "./geometry";
import type { ScoredWord } from "./scoring";
import { scoredWordsOf } from "./scoring";

export interface Prospect {
    readonly verdict: GeometryVerdict;
    readonly words: readonly ScoredWord[];
    readonly points: number;
    readonly bingo: boolean;
}

export function prospectOf(board: Board, draft: Draft, rules: TableRules): Prospect {
    const laid = laidOf(draft);
    const formation = formationOf(board, laid);
    if (formation.verdict !== "playable") {
        return { verdict: formation.verdict, words: [], points: 0, bingo: false };
    }
    const words = scoredWordsOf(board, laid, formation.words);
    const bingo = rules.rackSize !== null && laid.length === rules.rackSize;
    const wordPoints = words.reduce((sum, word) => sum + word.points, 0);
    return {
        verdict: "playable",
        words,
        points: wordPoints + (bingo ? rules.bingoBonus : 0),
        bingo,
    };
}
