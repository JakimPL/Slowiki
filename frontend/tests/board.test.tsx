import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Tile } from "../src/api/views";
import { Board } from "../src/table/Board";
import { aBoard, aTile } from "./positions";

const CENTER = 112;
const PASSIVE = {
    pending: new Map<number, Tile>(),
    targeting: false,
    onLay: null,
    onTakeBack: null,
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

    it("renders pending tiles as take-back buttons with the dashed mark", () => {
        const pending = new Map<number, Tile>([[CENTER, aTile({ letter: "K" })]]);
        const markup = renderToStaticMarkup(
            <Board
                board={aBoard()}
                pending={pending}
                targeting={false}
                onLay={() => undefined}
                onTakeBack={() => undefined}
            />,
        );
        expect(markup).toContain('data-pending="true"');
        expect(markup).toContain('role="group"');
        expect(markup).toContain('aria-label="Square 8·8"');
    });

    it("marks empty cells as targets while a tile is lifted", () => {
        const markup = renderToStaticMarkup(
            <Board
                board={aBoard()}
                pending={new Map<number, Tile>()}
                targeting={true}
                onLay={() => undefined}
                onTakeBack={null}
            />,
        );
        expect(markup).toContain("cell-target");
    });
});
