import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { reconciledTray, trayTilesOf } from "../src/play/tray";
import { Tray } from "../src/table/Tray";
import { stubBindings } from "./bindings";
import { aTile } from "./positions";

describe("tray model", () => {
    it("keeps only tiles that stay in the rack", () => {
        const rack = [aTile({ identifier: 1 }), aTile({ identifier: 2 })];
        expect(reconciledTray([2, 9], rack)).toEqual([2]);
        expect(reconciledTray([2], null)).toEqual([]);
        expect(trayTilesOf([2, 1], rack).map((tile) => tile.identifier)).toEqual([2, 1]);
    });
});

describe("Tray", () => {
    it("hints while empty and idle", () => {
        const markup = renderToStaticMarkup(
            <Tray
                tiles={[]}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings()}
                parkable={false}
                onPark={() => undefined}
            />,
        );
        expect(markup).toContain('data-region="tray"');
        expect(markup).toContain("Set tiles aside here");
        expect(markup).not.toContain("Park here");
    });

    it("offers a park slot while a tile rests elsewhere", () => {
        const markup = renderToStaticMarkup(
            <Tray
                tiles={[]}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings(7)}
                parkable={true}
                onPark={() => undefined}
            />,
        );
        expect(markup).toContain("Park here");
        expect(markup).not.toContain("Set tiles aside here");
    });

    it("shows parked tiles as grasp buttons", () => {
        const markup = renderToStaticMarkup(
            <Tray
                tiles={[aTile({ identifier: 4, letter: "W" })]}
                locked={new Set<number>()}
                incoming={null}
                bindings={stubBindings()}
                parkable={false}
                onPark={() => undefined}
            />,
        );
        expect(markup).toContain('data-tile="4"');
        expect(markup).toContain(">W<");
    });

    it("opens a landing slot for a tile carried in from the rack", () => {
        const markup = renderToStaticMarkup(
            <Tray
                tiles={[]}
                locked={new Set<number>()}
                incoming={{ carried: 4, before: null }}
                bindings={stubBindings(null, 4)}
                parkable={false}
                onPark={() => undefined}
            />,
        );
        expect(markup).toContain('data-drop="true"');
        expect(markup).toContain("slot-shadow");
        expect(markup).not.toContain("Set tiles aside here");
    });
});
