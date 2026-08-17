import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Rack } from "../src/table/Rack";
import { stubBindings } from "./bindings";
import { aTile } from "./positions";

const TILES = [aTile({ identifier: 1, letter: "K" }), aTile({ identifier: 2, letter: "O" })];

describe("Rack", () => {
    it("stays passive without bindings", () => {
        const markup = renderToStaticMarkup(
            <Rack tiles={TILES} liftedId={null} bindings={null} returnable={false} onReturn={() => undefined} />,
        );
        expect(markup).toContain('role="img"');
        expect(markup).not.toContain("<button");
    });

    it("offers each tile as a grasp button and marks the lifted one", () => {
        const markup = renderToStaticMarkup(
            <Rack tiles={TILES} liftedId={2} bindings={stubBindings()} returnable={false} onReturn={() => undefined} />,
        );
        expect(markup).toContain('role="group"');
        expect(markup).toContain('data-region="rack"');
        expect(markup).toContain('aria-label="Tile K · 1"');
        expect(markup).toContain('data-tile="1"');
        expect(markup).toContain('data-lifted="true"');
        expect(markup).toContain('aria-pressed="true"');
        expect(markup).not.toContain("Return here");
    });

    it("offers a return slot while a tray tile is lifted", () => {
        const markup = renderToStaticMarkup(
            <Rack tiles={TILES} liftedId={9} bindings={stubBindings()} returnable={true} onReturn={() => undefined} />,
        );
        expect(markup).toContain("Return here");
    });

    it("names blank tiles for assistive tech", () => {
        const blank = aTile({ identifier: 3, letter: "", value: 0, blank: true });
        const markup = renderToStaticMarkup(
            <Rack tiles={[blank]} liftedId={null} bindings={stubBindings()} returnable={false} onReturn={() => undefined} />,
        );
        expect(markup).toContain('aria-label="Blank tile"');
    });
});
