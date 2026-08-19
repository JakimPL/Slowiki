import { describe, expect, it } from "vitest";

import { EN } from "../../src/text/en";
import type { Catalog, PluralCategory } from "../../src/text/keys";
import { countedFrom, filled, textFrom } from "../../src/text/message";
import { PL } from "../../src/text/pl";

const CATALOGS: readonly Catalog[] = [EN, PL];

const CATEGORIES: readonly PluralCategory[] = ["one", "few", "many", "other"];

function placeholders(template: string): readonly string[] {
    return [...template.matchAll(/\{([a-z_]+)\}/g)].map((found) => found[1] ?? "").sort();
}

describe("filled", () => {
    it("substitutes named values and prints numbers", () => {
        expect(filled("{who} of {total}", { who: "one", total: 4 })).toBe("one of 4");
    });

    it("substitutes a placeholder wherever it repeats", () => {
        expect(filled("{word} — {word}", { word: "PIŁA" })).toBe("PIŁA — PIŁA");
    });

    it("refuses a placeholder the values leave out", () => {
        expect(() => filled("{missing}", {})).toThrow("Unknown placeholder missing");
    });
});

describe("textFrom", () => {
    it("reads a message that carries no placeholder", () => {
        expect(textFrom(EN, "arrive.code_label")).toBe("Table code");
    });

    it("fills a message from its values", () => {
        expect(textFrom(EN, "seats.gathering", { present: 1, total: 4 })).toBe(
            "Gathering players — 1 of 4 at the table",
        );
    });
});

describe("countedFrom", () => {
    it("chooses the category the count calls for", () => {
        expect(countedFrom(EN, "en", "hand.exchange_left", 1)).toBe("1 exchange left this game.");
        expect(countedFrom(EN, "en", "hand.exchange_left", 3)).toBe("3 exchanges left this game.");
    });

    it("fills the counted message from its own values", () => {
        expect(countedFrom(EN, "en", "seats.won", 1, { names: "Ala", points: 42 })).toBe("Ala wins with 42");
        expect(countedFrom(EN, "en", "seats.won", 2, { names: "Ala and Ola", points: 42 })).toBe(
            "Ala and Ola share the win with 42",
        );
    });
});

describe("every catalog", () => {
    it("carries a message for every key", () => {
        for (const catalog of CATALOGS) {
            const templates = [
                ...Object.values(catalog.plain),
                ...Object.values(catalog.plural).flatMap((entry) => Object.values(entry)),
            ];
            expect(templates.length).toBeGreaterThan(0);
            for (const template of templates) {
                expect(template.trim()).not.toBe("");
            }
        }
    });

    it("prints placeholders without their declared type", () => {
        for (const catalog of CATALOGS) {
            for (const template of Object.values(catalog.plain)) {
                expect(template).not.toContain(":number");
            }
        }
    });

    it("agrees on placeholders across the categories of one plural message", () => {
        for (const catalog of CATALOGS) {
            for (const entry of Object.values(catalog.plural)) {
                const named = CATEGORIES.map((category) => placeholders(entry[category]).join(","));
                expect(new Set(named).size).toBe(1);
            }
        }
    });

    it("carries the same placeholders as the reference for every key", () => {
        for (const key of Object.keys(EN.plain)) {
            const reference = EN.plain[key as keyof typeof EN.plain];
            const translated = PL.plain[key as keyof typeof PL.plain];
            expect(placeholders(translated)).toStrictEqual(placeholders(reference));
        }
    });
});

describe("the Polish catalog", () => {
    it("counts in three categories", () => {
        expect(countedFrom(PL, "pl", "hand.exchange_left", 1)).toBe("Została 1 wymiana w tej grze.");
        expect(countedFrom(PL, "pl", "hand.exchange_left", 3)).toBe("Zostały 3 wymiany w tej grze.");
        expect(countedFrom(PL, "pl", "hand.exchange_left", 7)).toBe("Zostało 7 wymian w tej grze.");
    });

    it("fills a translated message", () => {
        expect(textFrom(PL, "seats.gathering", { present: 1, total: 4 })).toBe("Zbieramy graczy — 1 z 4 przy stole");
    });
});
