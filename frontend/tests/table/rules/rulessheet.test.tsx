import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Composing } from "../../../src/play/rules/useComposing";
import { RulesSheet } from "../../../src/table/rules/RulesSheet";
import { someRules } from "../../fixtures/positions";
import { aComposing } from "../../fixtures/rules";

const NOTHING = (): void => undefined;

function markupOf(composing: Composing = aComposing()): string {
    return renderToStaticMarkup(<RulesSheet composing={composing} readOnly={false} onClose={NOTHING} />);
}

describe("RulesSheet", () => {
    it("holds one collapsed disclosure per group outside the card", () => {
        const markup = markupOf();
        expect(markup).toContain("Taking a turn");
        expect(markup).toContain("Scoring and ending");
        expect(markup).toContain("Letters and the board");
        expect(markup).not.toContain("The table");
        expect(markup).not.toContain('aria-expanded="true"');
        expect(markup).not.toContain("rules-group-rows");
    });

    it("names each group's state and rests the reset while nothing differs", () => {
        const markup = markupOf();
        expect(markup.match(/Standard/g)?.length).toBe(3);
        expect(markup).toContain("Back to the standard rules");
        expect(markup).toContain('disabled=""');
    });

    it("opens the group that holds a deviating rule and prints the standard", () => {
        const markup = markupOf(aComposing(someRules({ premoves: false })));
        expect(markup).toContain('aria-expanded="true"');
        expect(markup).toContain('data-deviating="true"');
        expect(markup).toContain("Standard: on");
        expect(markup).toContain("Put back");
        expect(markup).toContain("1 change");
    });

    it("draws each row from its kind", () => {
        const markup = markupOf(aComposing(someRules({ bingo_tiles: 6, board: "scrabble" })));
        expect(markup).toContain("stepper");
        expect(markup).toContain("menu-options");
        expect(markup).toContain("Tiles a bonus play must use");
        expect(markup).toContain("Board");
    });

    it("keeps the expert switch out of sight while no setting is expert", () => {
        expect(markupOf()).not.toContain("Expert settings");
    });
});
