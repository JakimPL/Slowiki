import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { storyFor } from "../../../src/play/story/story";
import { GameOver } from "../../../src/table/sheets/GameOver";
import { aCompany, aSeatView, aView } from "../../fixtures/positions";

const NOBODY = (): void => {
    throw new Error("nobody acts in a static render");
};

const NAMES = ["Ala", "Ola", "Ela", "Ula"];

function anEnding(mySeat: number | null, scores: Record<number, number>): string {
    const players = Object.keys(scores).map(Number);
    const view = aView({ phase: "game_over", scores, players });
    const company = aCompany(players.map((seat) => aSeatView(seat, { name: NAMES[seat] ?? null })));
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
        expect(standing).toContain('data-podium="1"');
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
        expect(markup.match(/data-podium="1"/g)).toHaveLength(2);
    });

    it("marks where the player landed", () => {
        const standing = anEnding(1, { 0: 42, 1: 30 });
        expect(standing).toContain("you</em>");
        expect(standing).not.toContain("You win!");
    });

    it("raises the whole podium only once four players sat down", () => {
        const three = anEnding(0, { 0: 30, 1: 42, 2: 12 });
        expect(three.match(/data-podium="\d"/g)).toEqual(['data-podium="1"']);
        const four = anEnding(0, { 0: 30, 1: 42, 2: 12, 3: 20 });
        expect(four.match(/data-podium="\d"/g)).toEqual(['data-podium="1"', 'data-podium="2"', 'data-podium="3"']);
    });

    it("offers both ways out of the standing", () => {
        const markup = anEnding(0, { 0: 30, 1: 42 });
        expect(markup).toContain("Close</button>");
        expect(markup).toContain("Leave the table</button>");
        expect(markup).toContain('aria-label="Close the final standing"');
    });
});
