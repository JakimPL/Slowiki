import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Tile } from "../src/api/views";
import { Board } from "../src/table/Board";
import { stubBindings } from "./bindings";
import { aBoard, aTile } from "./positions";

const CENTER = 112;
const PASSIVE = {
    pending: new Map<number, Tile>(),
    targeting: false,
    dropCell: null,
    fresh: new Set<number>(),
    freshTint: null,
    onLay: null,
    bindings: null,
};

describe("Board", () => {
    it("renders premiums, the center star, and placed tiles", () => {
        const board = aBoard(
            { 0: aTile({ letter: "W", value: 5, category: "green" }) },
            {
                1: { kind: "word_multiplier", multiplier: 2, category: null },
                2: { kind: "letter_multiplier", multiplier: 3, category: null },
                3: { kind: "category_multiplier", multiplier: 3, category: "yellow" },
            },
        );
        const markup = renderToStaticMarkup(<Board board={board} {...PASSIVE} />);
        expect(markup).toContain("2×");
        expect(markup).toContain("×3");
        expect(markup).toContain("✦");
        expect(markup).toContain(">W<");
        expect(markup).toContain("--tile-face-green");
        expect(markup).toContain("--category-yellow-fill");
        expect(markup).toContain("--premium-word-2-fill");
        expect(markup).toContain("--premium-letter-3-fill");
    });

    it("keeps the star over the center premium fill", () => {
        const board = aBoard({}, { [CENTER]: { kind: "category_multiplier", multiplier: 3, category: "red" } });
        const markup = renderToStaticMarkup(<Board board={board} {...PASSIVE} />);
        expect(markup).toContain("✦");
        expect(markup).toContain("--category-red-fill");
    });

    it("marks blanks with a hollow diamond and hides the zero value", () => {
        const board = aBoard({ 0: aTile({ letter: "", value: 0, blank: true }) });
        const markup = renderToStaticMarkup(<Board board={board} {...PASSIVE} />);
        expect(markup).toContain("◇");
        expect(markup).not.toContain("tile-value");
    });

    it("renders pending tiles as grasp buttons with the dashed mark", () => {
        const pending = new Map<number, Tile>([[CENTER, aTile({ letter: "K" })]]);
        const markup = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} pending={pending} bindings={stubBindings()} />,
        );
        expect(markup).toContain('data-pending="true"');
        expect(markup).toContain('role="group"');
        expect(markup).toContain('data-region="board"');
    });

    it("marks empty cells as targets while a tile is lifted", () => {
        const markup = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} targeting={true} onLay={() => undefined} />,
        );
        expect(markup).toContain("cell-target");
        expect(markup).toContain('aria-label="Square 8·8"');
    });

    it("rings the computed drop cell while carrying", () => {
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={aBoard()} dropCell={CENTER} />);
        expect(markup).toContain('data-drop="true"');
    });

    it("rings the fresh play in the mover's tint", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }) });
        const markup = renderToStaticMarkup(
            <Board {...PASSIVE} board={board} fresh={new Set([CENTER])} freshTint="#c95b79" />,
        );
        expect(markup).toContain('data-fresh="true"');
        expect(markup).toContain("--fresh:#c95b79");
    });
});
