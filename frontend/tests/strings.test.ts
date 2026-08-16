import { describe, expect, it } from "vitest";

import {
    captionFor,
    gatheringCaption,
    nameFor,
    offeringCaption,
    thinkingCaption,
    wonCaption,
} from "../src/table/strings";
import { aCompany, aSeatView } from "./positions";

describe("nameFor", () => {
    it("prefers the served name and falls back to a numbered player", () => {
        const company = aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1), aSeatView(2, { claimed: false })]);
        expect(nameFor(company, 0)).toBe("Ala");
        expect(nameFor(company, 1)).toBe("Player 2");
        expect(nameFor(company, 2)).toBe("Open seat");
    });
});

describe("captions", () => {
    it("narrates thinking players", () => {
        expect(thinkingCaption(["Ala"])).toBe("Ala is thinking…");
        expect(thinkingCaption(["Ala", "Ola"])).toBe("Ala and Ola are thinking…");
        expect(thinkingCaption(["Ala", "Ola", "Jan"])).toBe("Ala, Ola and Jan are thinking…");
    });

    it("narrates wins and shared wins", () => {
        expect(wonCaption(["Ala"], 42)).toBe("Ala wins with 42");
        expect(wonCaption(["Ala", "Ola"], 42)).toBe("Ala and Ola share the win with 42");
    });

    it("counts the gathering", () => {
        expect(gatheringCaption(1, 4)).toBe("Gathering players — 1 of 4 at the table");
    });

    it("describes offerings with their player span", () => {
        expect(offeringCaption("literaki", 2, 8)).toBe("literaki · 2–8 players");
        expect(offeringCaption("solo-literaki", 1, 1)).toBe("solo-literaki · 1 player");
    });
});

describe("captionFor", () => {
    it("announces my turn", () => {
        expect(captionFor({ kind: "acting", seats: [0], points: null }, aCompany())).toBe("Your turn");
    });

    it("names the watched actors", () => {
        expect(captionFor({ kind: "watching", seats: [1], points: null }, aCompany())).toBe("Ola is thinking…");
    });
});
