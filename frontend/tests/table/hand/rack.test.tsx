import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Rack } from "../../../src/table/hand/Rack";
import { stubBindings } from "../../fixtures/bindings";
import { aTile } from "../../fixtures/positions";

const TILES = [aTile({ identifier: 1, letter: "K" }), aTile({ identifier: 2, letter: "O" })];

describe("Rack", () => {
    it("stays passive without bindings", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set<number>()}
                incoming={null}
                bindings={null}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('role="img"');
        expect(markup).not.toContain("<button");
    });

    it("offers each tile as a grasp button and marks the lifted one", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings(2)}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('role="group"');
        expect(markup).toContain('data-region="rack"');
        expect(markup).toContain('aria-label="Tile K · 1"');
        expect(markup).toContain('data-tile="1"');
        expect(markup).toContain('data-lifted="true"');
        expect(markup).toContain('aria-pressed="true"');
        expect(markup).not.toContain("Return here");
    });

    it("offers a return slot while a tile rests elsewhere", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings(9)}
                returnable={true}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain("Return here");
    });

    it("shows committed tiles as inert ghost faces", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set([1])}
                incoming={null}
                bindings={stubBindings()}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('data-ghost="true"');
        expect(markup).not.toContain('data-tile="1"');
        expect(markup).toContain('data-tile="2"');
    });

    it("dims the carried tile and shows the slot it would land in", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set<number>()}
                incoming={{ carried: 2, before: 1 }}
                bindings={stubBindings(null, 2)}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('data-drop="true"');
        expect(markup).toContain("slot-shadow");
        expect(markup.indexOf("slot-shadow")).toBeLessThan(markup.indexOf('data-tile="1"'));
        expect(markup).not.toContain('data-tile="2"');
    });

    it("marks the carried tile while the carry hangs over another region", () => {
        const markup = renderToStaticMarkup(
            <Rack
                tiles={TILES}
                capacity={7}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings(null, 2)}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('data-carried="true"');
        expect(markup).not.toContain("slot-shadow");
    });

    it("names blank tiles for assistive tech", () => {
        const blank = aTile({ identifier: 3, letter: "", value: 0, blank: true });
        const markup = renderToStaticMarkup(
            <Rack
                tiles={[blank]}
                capacity={7}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings()}
                returnable={false}
                onReturn={() => undefined}
            />,
        );
        expect(markup).toContain('aria-label="Blank tile"');
    });
});
