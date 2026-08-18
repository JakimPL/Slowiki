import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { storyFor } from "../../../src/play/story/story";
import { GameOver } from "../../../src/table/sheets/GameOver";
import { aCompany, aView } from "../../fixtures/positions";

const NOBODY = (): void => {
    throw new Error("nobody acts in a static render");
};

describe("GameOver", () => {
    it("ranks the standing and crowns the winner", () => {
        const view = aView({ phase: "game_over", scores: { 0: 30, 1: 42 } });
        const company = aCompany();
        const story = storyFor(view, company, 0);
        const markup = renderToStaticMarkup(
            <GameOver view={view} company={company} story={story} onClose={NOBODY} onLeave={NOBODY} />,
        );
        expect(markup).toContain("Game over");
        expect(markup).toContain("Ola wins with 42");
        const standing = markup.slice(markup.indexOf("<ol"));
        expect(standing.indexOf("Ola")).toBeLessThan(standing.indexOf("Ala"));
        expect(markup).toContain("30");
    });

    it("offers both ways out of the standing", () => {
        const view = aView({ phase: "game_over", scores: { 0: 30, 1: 42 } });
        const company = aCompany();
        const markup = renderToStaticMarkup(
            <GameOver
                view={view}
                company={company}
                story={storyFor(view, company, 0)}
                onClose={NOBODY}
                onLeave={NOBODY}
            />,
        );
        expect(markup).toContain("Close</button>");
        expect(markup).toContain("Leave the table</button>");
        expect(markup).toContain('aria-label="Close the final standing"');
    });
});
