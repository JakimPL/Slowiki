import { describe, expect, it } from "vitest";

import { storyFor } from "../src/play/story";
import { aCompany, aSeatView, aView } from "./positions";

describe("storyFor", () => {
    it("crowns the top score when the game is over", () => {
        const view = aView({ phase: "game_over", scores: { 0: 30, 1: 42 } });
        const story = storyFor(view, aCompany(), 0);
        expect(story).toEqual({ kind: "over", seats: [1], points: 42 });
    });

    it("shares the win between tied players", () => {
        const view = aView({ phase: "game_over", scores: { 0: 42, 1: 42 } });
        expect(storyFor(view, aCompany(), null).seats).toEqual([0, 1]);
    });

    it("reports acting when I am among the actors", () => {
        const story = storyFor(aView({ to_act: [0, 1] }), aCompany(), 0);
        expect(story.kind).toBe("acting");
        expect(story.seats).toEqual([0, 1]);
    });

    it("prefers acting over gathering", () => {
        const company = aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]);
        expect(storyFor(aView({ to_act: [0] }), company, 0).kind).toBe("acting");
    });

    it("reports gathering while seats stay unclaimed", () => {
        const company = aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]);
        expect(storyFor(aView({ to_act: [1] }), company, 0).kind).toBe("gathering");
    });

    it("watches the sorted actors otherwise", () => {
        const story = storyFor(aView({ to_act: [1, 0] }), aCompany(), null);
        expect(story.kind).toBe("watching");
        expect(story.seats).toEqual([0, 1]);
    });
});
