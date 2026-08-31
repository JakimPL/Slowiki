import { describe, expect, it } from "vitest";

import {
    captionFor,
    categoryCaption,
    choiceCaption,
    gatheringCaption,
    nameFor,
    thinkingCaption,
    wonCaption,
} from "../../src/table/strings";
import { aCompany, aSeatView } from "../fixtures/positions";

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
});

describe("captionFor", () => {
    it("announces my turn", () => {
        expect(captionFor({ kind: "acting", seats: [0], points: null, mine: true }, aCompany())).toBe("Your turn");
    });

    it("hands the win to the player who took it", () => {
        expect(captionFor({ kind: "over", seats: [0], points: 42, mine: true }, aCompany())).toBe("You win with 42");
        expect(captionFor({ kind: "over", seats: [0, 1], points: 42, mine: true }, aCompany())).toBe(
            "You share the win with 42",
        );
        expect(captionFor({ kind: "over", seats: [1], points: 42, mine: false }, aCompany())).toBe("Ola wins with 42");
    });

    it("names the watched actors", () => {
        expect(captionFor({ kind: "watching", seats: [1], points: null, mine: false }, aCompany())).toBe(
            "Ola is thinking…",
        );
    });
});

describe("identifier captions", () => {
    it("says a category and a choice in words", () => {
        expect(categoryCaption("yellow")).toBe("Yellow");
        expect(choiceCaption("sjp")).toBe("Polish (SJP)");
        expect(choiceCaption("scrabble-en")).toBe("Scrabble (English)");
    });

    it("keeps an identifier it has no word for", () => {
        expect(categoryCaption("teal")).toBe("teal");
        expect(choiceCaption("hexagonal")).toBe("hexagonal");
    });
});
