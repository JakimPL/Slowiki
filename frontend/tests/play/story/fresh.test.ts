import { describe, expect, it } from "vitest";

import { BEFORE_ANY_TURN, freshMarks } from "../../../src/play/story/fresh";
import { aPlayRecord } from "../../fixtures/positions";

const MY_SEAT = 0;
const OPPONENT = 1;

describe("freshMarks", () => {
    it("numbers the played squares along the reading of the word", () => {
        const play = aPlayRecord({ player: OPPONENT, indices: [114, 112, 113] });
        const marks = freshMarks(play, MY_SEAT, BEFORE_ANY_TURN);
        expect(marks.get(112)?.ordinal).toBe(0);
        expect(marks.get(113)?.ordinal).toBe(1);
        expect(marks.get(114)?.ordinal).toBe(2);
    });

    it("waves an opponent's newest play at every one of its squares", () => {
        const play = aPlayRecord({ player: OPPONENT, indices: [112, 113], turn_number: 4 });
        const marks = freshMarks(play, MY_SEAT, BEFORE_ANY_TURN);
        expect([...marks.values()].every((mark) => mark.waving)).toBe(true);
    });

    it("rests once the play is acknowledged", () => {
        const play = aPlayRecord({ player: OPPONENT, turn_number: 4 });
        const marks = freshMarks(play, MY_SEAT, 4);
        expect([...marks.values()].every((mark) => mark.waving)).toBe(false);
        expect(marks.size).toBe(play.indices.length);
    });

    it("wakes again for the play that follows the acknowledged one", () => {
        const play = aPlayRecord({ player: OPPONENT, turn_number: 5 });
        const marks = freshMarks(play, MY_SEAT, 4);
        expect([...marks.values()].every((mark) => mark.waving)).toBe(true);
    });

    it("rests on my own play", () => {
        const play = aPlayRecord({ player: MY_SEAT, turn_number: 4 });
        const marks = freshMarks(play, MY_SEAT, BEFORE_ANY_TURN);
        expect([...marks.values()].every((mark) => mark.waving)).toBe(false);
    });

    it("marks nothing before the first play", () => {
        expect(freshMarks(null, MY_SEAT, BEFORE_ANY_TURN).size).toBe(0);
    });
});
