import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Tile } from "../../../src/api/views";
import type { FreshMark } from "../../../src/play/story/fresh";
import { Board } from "../../../src/table/board/Board";
import { stubBindings } from "../../fixtures/bindings";
import { aBoard, aTile } from "../../fixtures/positions";

const CENTER = 112;
const PASSIVE = {
    pending: new Map<number, Tile>(),
    ghosts: new Map<number, Tile>(),
    targeting: false,
    dropCell: null,
    fresh: new Map<number, FreshMark>(),
    freshFrame: null,
    freshTint: null,
    freshWaving: false,
    onLay: null,
    bindings: null,
    hold: null,
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
        expect(markup).toContain("tile-blank");
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

    it("raises a lifted pending tile and dims a carried one", () => {
        const pending = new Map<number, Tile>([[CENTER, aTile({ identifier: 7, letter: "K" })]]);
        const lifted = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} pending={pending} bindings={stubBindings(7)} />,
        );
        expect(lifted).toContain('data-lifted="true"');
        const carried = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} pending={pending} bindings={stubBindings(null, 7)} />,
        );
        expect(carried).toContain('data-carried="true"');
    });

    it("keeps a premium lit under a tile that is still being placed", () => {
        const board = aBoard({}, { [CENTER]: { kind: "letter_multiplier", multiplier: 3, category: null } });
        const pending = new Map<number, Tile>([[CENTER, aTile({ identifier: 7, letter: "K" })]]);
        const carried = renderToStaticMarkup(
            <Board {...PASSIVE} board={board} pending={pending} bindings={stubBindings(null, 7)} />,
        );
        expect(carried).toContain("--premium-letter-3-fill");
        expect(carried).toContain('data-carried="true"');
    });

    it("keeps a premium lit under a queued premove ghost", () => {
        const board = aBoard({}, { 0: { kind: "category_multiplier", multiplier: 3, category: "yellow" } });
        const ghosts = new Map<number, Tile>([[0, aTile({ letter: "K" })]]);
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={board} ghosts={ghosts} />);
        expect(markup).toContain("--category-yellow-fill");
        expect(markup).toContain('data-ghost="true"');
    });

    it("covers a spent premium with the tile standing on it", () => {
        const board = aBoard(
            { 0: aTile({ letter: "W" }) },
            { 0: { kind: "word_multiplier", multiplier: 2, category: null } },
        );
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={board} />);
        expect(markup).toContain(">W<");
        expect(markup).not.toContain("--premium-word-2-fill");
    });

    it("marks empty cells as targets while a tile is lifted", () => {
        const markup = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} targeting={true} onLay={() => undefined} />,
        );
        expect(markup).toContain("cell-target");
        expect(markup).toContain('aria-label="Square 8·8"');
    });

    it("renders queued premove ghosts as untargetable translucent faces", () => {
        const ghosts = new Map<number, Tile>([[CENTER, aTile({ letter: "K" })]]);
        const markup = renderToStaticMarkup(
            <Board {...PASSIVE} board={aBoard()} ghosts={ghosts} targeting={true} onLay={() => undefined} />,
        );
        expect(markup).toContain('data-ghost="true"');
        expect(markup).not.toContain('aria-label="Square 8·8"');
    });

    it("rings the computed drop cell while carrying", () => {
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={aBoard()} dropCell={CENTER} />);
        expect(markup).toContain('data-drop="true"');
    });

    it("announces the hold duration while the board answers for its words", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }) });
        const hold = {
            held: CENTER,
            press: () => undefined,
            release: () => undefined,
            consumed: () => undefined,
        };
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={board} hold={hold} />);
        expect(markup).toContain("--hold:450ms");
        expect(markup).toContain('data-holding="true"');
    });

    it("leaves standing tiles quiet where the panel is not offered", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }) });
        const markup = renderToStaticMarkup(<Board {...PASSIVE} board={board} />);
        expect(markup).not.toContain("--hold");
        expect(markup).not.toContain("data-holding");
    });

    it("frames the fresh play once, in the mover's tint", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }), [CENTER + 1]: aTile({ letter: "Ó" }) });
        const markup = renderToStaticMarkup(
            <Board
                {...PASSIVE}
                board={board}
                fresh={
                    new Map([
                        [CENTER, { ordinal: 0, waving: false }],
                        [CENTER + 1, { ordinal: 1, waving: false }],
                    ])
                }
                freshFrame={{ row: 7, column: 7, rows: 1, columns: 2 }}
                freshTint="#af4a54"
            />,
        );
        expect(markup).toContain("--fresh:#af4a54");
        expect(markup.match(/board-fresh/g)).toHaveLength(1);
        expect(markup).toContain("--frame-row:7");
        expect(markup).toContain("--frame-column:7");
        expect(markup).toContain("--frame-rows:1");
        expect(markup).toContain("--frame-columns:2");
        expect(markup).toContain('data-fresh="true"');
        expect(markup).not.toContain("data-waving");
        expect(markup).not.toContain("board-sweep");
    });

    it("lays the sweeping light over the tiles and keeps the frame under them", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }) });
        const markup = renderToStaticMarkup(
            <Board
                {...PASSIVE}
                board={board}
                fresh={new Map([[CENTER, { ordinal: 0, waving: true }]])}
                freshFrame={{ row: 7, column: 7, rows: 1, columns: 1 }}
                freshWaving
            />,
        );
        expect(markup.indexOf("board-fresh")).toBeLessThan(markup.indexOf("board-sweep"));
    });

    it("carries each waving tile its place along the play", () => {
        const board = aBoard({ [CENTER]: aTile({ letter: "W" }), [CENTER + 1]: aTile({ letter: "Ó" }) });
        const markup = renderToStaticMarkup(
            <Board
                {...PASSIVE}
                board={board}
                fresh={
                    new Map([
                        [CENTER, { ordinal: 0, waving: true }],
                        [CENTER + 1, { ordinal: 1, waving: true }],
                    ])
                }
                freshTint="#af4a54"
            />,
        );
        expect(markup).toContain('data-waving="true"');
        expect(markup).toContain("--ordinal:0");
        expect(markup).toContain("--ordinal:1");
    });
});
