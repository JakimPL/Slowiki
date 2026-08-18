import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { openedFrom } from "../../src/play/live/events";
import { SettingsProvider } from "../../src/play/settings/useSettings";
import { Table } from "../../src/table/Table";
import { aBoard, aCompany, aPlayRecord, aSeatView, aTableResponse, aTile, aView } from "../fixtures/positions";

const ARRIVAL = { seat: { table: "t1", token: "tok-1" }, code: "KWPZTR", seated: 0 };

describe("Table", () => {
    it("shows the gathering room with the code and no tiles while seats stay open", () => {
        const response = aTableResponse({
            view: aView({ to_act: [0], racks: { 0: null, 1: null } }),
            company: aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]),
        });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain("Gathering players — 1 of 2 at the table");
        expect(markup).toContain("KWPZTR");
        expect(markup).toContain("Copy invitation");
        expect(markup).not.toContain("tile-letter");
        expect(markup).not.toContain("Your turn");
        expect(markup).toContain("Bag 80");
    });

    it("marks my turn on the frame once the table is full", () => {
        const response = aTableResponse({ view: aView({ to_act: [0] }) });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain("Your turn");
        expect(markup).toContain('data-acting="true"');
        expect(markup).not.toContain("Gathering players");
    });

    it("offers the desk controls to a seated player", () => {
        const response = aTableResponse({ view: aView({ to_act: [0] }) });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain(">Play</button>");
        expect(markup).toContain(">Pass</button>");
        expect(markup).toContain(">Shuffle</button>");
        expect(markup).not.toContain(">Recall</button>");
        expect(markup).toContain('class="rack" role="group"');
        expect(markup).toContain('data-region="tray"');
        expect(markup).toContain('class="side"');
        expect(markup).toContain('aria-label="Players"');
        expect(markup).toContain("--row-count:1");
        expect(markup).toContain('name="docket"');
        expect(markup).toContain("Notify me when my turn comes while this tab rests");
        expect(markup).toContain('aria-pressed="false"');
    });

    it("mirrors a queued premove as ghosts, a chip with Cancel, and a resting rack", () => {
        const response = aTableResponse({
            view: aView({
                to_act: [1],
                racks: { 0: [aTile({ identifier: 7, letter: "K" }), aTile({ identifier: 9, letter: "O" })], 1: null },
                premove: {
                    player: 0,
                    action: { kind: "play", placements: [{ tile_id: 7, row: 7, column: 7, letter: null }] },
                },
                pending_premoves: [0],
            }),
        });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain('data-ghost="true"');
        expect(markup).toContain("Premove queued");
        expect(markup).toContain(">Cancel</button>");
        expect(markup).not.toContain('data-tile="7"');
    });

    it("keeps Pass for the acting turn only", () => {
        const response = aTableResponse({ view: aView({ to_act: [1] }) });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain('disabled="">Pass</button>');
    });

    it("surfaces a returned premove with its humanized reason", () => {
        const response = aTableResponse({ view: aView({ to_act: [0] }) });
        const state = {
            ...openedFrom(response),
            log: [
                {
                    seq: 3,
                    actor: 0,
                    kind: "premove-returned" as const,
                    words: [],
                    points: null,
                    reason: "invalid_word",
                },
            ],
        };
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={state}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain("Premove returned — invalid word.");
    });

    it("rings the last play in the mover's tint", () => {
        const response = aTableResponse({
            view: aView({
                board: aBoard({ 112: aTile({ letter: "W" }) }),
                last_play: aPlayRecord({ player: 1, indices: [112] }),
            }),
        });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain('data-fresh="true"');
        expect(markup).toContain('data-waving="true"');
    });

    it("keeps the desk away from spectators", () => {
        const response = aTableResponse({ view: aView({ racks: { 0: null, 1: null } }) });
        const spectator = { seat: { table: "t1", token: null }, code: null, seated: null };
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={spectator}
                    connection="live"
                    state={openedFrom(response)}
                    clock={null}
                    trouble={null}
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).not.toContain(">Play</button>");
        expect(markup).not.toContain("rack-tile");
    });

    it("surfaces the connection chip and reads the trouble in the feedback slot", () => {
        const response = aTableResponse();
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="resuming"
                    state={openedFrom(response)}
                    clock={null}
                    trouble="stream lost"
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain("Reconnecting");
        expect(markup).toContain('data-tone="danger">stream lost');
        expect(markup).not.toContain('class="trouble"');
    });

    it("keeps the trouble line under the room while the table gathers", () => {
        const response = aTableResponse({
            company: aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]),
        });
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Table
                    arrival={ARRIVAL}
                    connection="lost"
                    state={openedFrom(response)}
                    clock={null}
                    trouble="stream lost"
                    onOutdated={() => Promise.resolve(null)}
                />
            </SettingsProvider>,
        );
        expect(markup).toContain('class="trouble">stream lost');
        expect(markup).not.toContain("feedback");
    });
});
