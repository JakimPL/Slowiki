import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { openedFrom } from "../src/play/events";
import { Table } from "../src/table/Table";
import { aCompany, aSeatView, aTableResponse, aView } from "./positions";

const ARRIVAL = { seat: { table: "t1", token: "tok-1" }, code: "KWPZTR", seated: 0 };

describe("Table", () => {
    it("shows the gathering room with the code and no tiles while seats stay open", () => {
        const response = aTableResponse({
            view: aView({ to_act: [0], racks: { 0: null, 1: null } }),
            company: aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]),
        });
        const markup = renderToStaticMarkup(
            <Table arrival={ARRIVAL} connection="live" state={openedFrom(response)} trouble={null} />,
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
            <Table arrival={ARRIVAL} connection="live" state={openedFrom(response)} trouble={null} />,
        );
        expect(markup).toContain("Your turn");
        expect(markup).toContain('data-acting="true"');
        expect(markup).not.toContain("Gathering players");
    });

    it("offers the desk controls to a seated player", () => {
        const response = aTableResponse({ view: aView({ to_act: [0] }) });
        const markup = renderToStaticMarkup(
            <Table arrival={ARRIVAL} connection="live" state={openedFrom(response)} trouble={null} />,
        );
        expect(markup).toContain(">Play</button>");
        expect(markup).toContain(">Pass</button>");
        expect(markup).toContain(">Recall</button>");
        expect(markup).toContain('class="rack" role="group"');
    });

    it("keeps the desk away from spectators", () => {
        const response = aTableResponse({ view: aView({ racks: { 0: null, 1: null } }) });
        const spectator = { seat: { table: "t1", token: null }, code: null, seated: null };
        const markup = renderToStaticMarkup(
            <Table arrival={spectator} connection="live" state={openedFrom(response)} trouble={null} />,
        );
        expect(markup).not.toContain(">Play</button>");
        expect(markup).not.toContain("rack-tile");
    });

    it("surfaces the connection chip when the stream drops", () => {
        const response = aTableResponse();
        const markup = renderToStaticMarkup(
            <Table arrival={ARRIVAL} connection="resuming" state={openedFrom(response)} trouble="stream lost" />,
        );
        expect(markup).toContain("Reconnecting");
        expect(markup).toContain("stream lost");
    });
});
