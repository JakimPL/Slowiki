import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { storyFor } from "../../../src/play/story/story";
import { GameOver } from "../../../src/table/sheets/GameOver";
import { aCompany, aView } from "../../fixtures/positions";

const NOBODY = (): void => {
    throw new Error("nobody acts in a static render");
};

function anEnding(mySeat: number | null, scores: Record<number, number>): string {
    const view = aView({ phase: "game_over", scores });
    const company = aCompany();
    return renderToStaticMarkup(
        <GameOver
            view={view}
            company={company}
            story={storyFor(view, company, mySeat)}
            mySeat={mySeat}
            onClose={NOBODY}
            onLeave={NOBODY}
        />,
    );
}

describe("GameOver", () => {
    it("ranks the standing and crowns the winner", () => {
        const markup = anEnding(0, { 0: 30, 1: 42 });
        expect(markup).toContain("Game over");
        expect(markup).toContain("Ola wins with 42");
        const standing = markup.slice(markup.indexOf("<ol"));
        expect(standing.indexOf("Ola")).toBeLessThan(standing.indexOf("Ala"));
        expect(standing).toContain('data-crowned="true"');
        expect(markup).toContain("30");
    });

    it("celebrates the win when it is the player's own", () => {
        const markup = anEnding(0, { 0: 42, 1: 30 });
        expect(markup).toContain("You win!");
        expect(markup).toContain('data-mine="true"');
        expect(markup).not.toContain("game-over-verdict");
    });

    it("spells out a win the player only shares", () => {
        const markup = anEnding(0, { 0: 42, 1: 42 });
        expect(markup).toContain("You share the win with 42");
        expect(markup.match(/data-crowned/g)).toHaveLength(2);
    });

    it("marks where the player landed", () => {
        const standing = anEnding(1, { 0: 42, 1: 30 });
        expect(standing).toContain("you</em>");
        expect(standing).not.toContain("You win!");
    });

    it("offers both ways out of the standing", () => {
        const markup = anEnding(0, { 0: 30, 1: 42 });
        expect(markup).toContain("Close</button>");
        expect(markup).toContain("Leave the table</button>");
        expect(markup).toContain('aria-label="Close the final standing"');
    });
});
