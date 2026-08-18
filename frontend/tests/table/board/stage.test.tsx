import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { BoardStage } from "../../../src/table/board/BoardStage";

const QUIET = (): void => undefined;

describe("BoardStage", () => {
    it("frames the board in a stage that carries the transform", () => {
        const markup = renderToStaticMarkup(
            <BoardStage onZoom={QUIET}>
                <div className="board" />
            </BoardStage>,
        );
        expect(markup).toContain("board-frame");
        expect(markup).toContain("board-stage");
        const frame = markup.indexOf("board-frame");
        expect(frame).toBeLessThan(markup.indexOf("board-stage"));
        expect(markup.indexOf("board-stage")).toBeLessThan(markup.indexOf('class="board"'));
    });

    it("keeps the fit control away while the board sits at its fitted size", () => {
        const markup = renderToStaticMarkup(
            <BoardStage onZoom={QUIET}>
                <div className="board" />
            </BoardStage>,
        );
        expect(markup).not.toContain("board-fit");
    });
});
