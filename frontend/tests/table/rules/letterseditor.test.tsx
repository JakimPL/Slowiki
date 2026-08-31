import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { AlphabetPreset, DistributionPreset } from "../../../src/api/tables";
import { LettersEditor } from "../../../src/table/rules/LettersEditor";
import { someRules } from "../../fixtures/positions";
import { aComposing } from "../../fixtures/rules";

const ALPHABET: AlphabetPreset = {
    name: "literaki",
    order: ["A", "B", "C"],
    dictionaries: ["sjp"],
    classes: [
        { value: 1, category: "yellow", letters: ["A"] },
        { value: 3, category: "blue", letters: ["B", "C"] },
    ],
};

const PLAIN: AlphabetPreset = {
    name: "scrabble-en",
    order: ["A", "B"],
    dictionaries: ["english"],
    classes: [{ value: 1, category: "standard", letters: ["A", "B"] }],
};

const DISTRIBUTION: DistributionPreset = { name: "polish", counts: { "9": ["A"], "2": ["B", "C"] } };

function markupOf(alphabet: AlphabetPreset, letters: Record<string, object> = {}): string {
    return renderToStaticMarkup(
        <LettersEditor
            composing={aComposing(someRules({ letters, blanks: 2 }))}
            alphabet={alphabet}
            distribution={DISTRIBUTION}
            minimum={0}
            maximum={99}
            step={1}
            readOnly={false}
        />,
    );
}

describe("LettersEditor", () => {
    it("prints a tile face and a count for every letter", () => {
        const markup = markupOf(ALPHABET);
        expect(markup.match(/letters-cell/g)?.length).toBe(3);
        expect(markup).toContain("×9");
        expect(markup).toContain("×2");
    });

    it("counts the whole bag, blanks and all", () => {
        expect(markupOf(ALPHABET)).toContain("15 tiles in the bag");
    });

    it("holds the selected letter's three facts over the grid", () => {
        const markup = markupOf(ALPHABET);
        expect(markup).toContain("Points");
        expect(markup).toContain("In the bag");
        expect(markup).toContain("Color");
    });

    it("offers a whole color only where the letters carry more than one", () => {
        expect(markupOf(ALPHABET)).toContain("Points for a whole color");
        expect(markupOf(PLAIN)).not.toContain("Points for a whole color");
        expect(markupOf(PLAIN)).not.toContain("Color</span>");
    });

    it("names a color in the reader's own words", () => {
        const markup = markupOf(ALPHABET);
        expect(markup).toContain("Yellow");
        expect(markup).toContain("Blue");
        expect(markup).not.toContain(">yellow<");
    });

    it("marks the letters an adjustment touches", () => {
        const markup = markupOf(ALPHABET, { B: { value: 12, count: 3 } });
        expect(markup).toContain('data-changed="true"');
        expect(markup).toContain("×3");
        expect(markup).toContain("16 tiles in the bag");
    });
});
