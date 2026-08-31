import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CreateCard } from "../../../src/table/arrive/CreateCard";
import { someRules } from "../../fixtures/positions";
import { aComposing } from "../../fixtures/rules";

const NOTHING = (): void => undefined;

function markupOf(composing = aComposing()): string {
    return renderToStaticMarkup(
        <CreateCard composing={composing} busy={false} named={true} onCreate={NOTHING} onOpenRules={NOTHING} />,
    );
}

describe("CreateCard", () => {
    it("carries the same five controls whatever is chosen", () => {
        const markup = markupOf();
        for (const label of ["Game", "Players", "Time per player", "Bonus per move", "House rules"]) {
            expect(markup).toContain(label);
        }
    });

    it("offers the seats and the clock rungs the server allows", () => {
        const markup = markupOf();
        expect(markup).toContain('value="8"');
        expect(markup).toContain("10 min");
        expect(markup).toContain("untimed");
    });

    it("reads as standard while the record matches its scheme", () => {
        const markup = markupOf();
        expect(markup).toContain("Standard");
        expect(markup).not.toContain("rules-chip");
    });

    it("counts and names the rules the card does not itself show", () => {
        const markup = markupOf(aComposing(someRules({ premoves: false, bingo_tiles: 6 })));
        expect(markup).toContain("2 changes");
        expect(markup).toContain("Queued moves · off");
        expect(markup).toContain("Tiles a bonus play must use · 6");
    });

    it("leaves its own controls out of the count they already show", () => {
        const markup = markupOf(aComposing(someRules({ seats: 4, total_seconds: 600 })));
        expect(markup).toContain("Standard");
        expect(markup).not.toContain("rules-chip");
    });
});
