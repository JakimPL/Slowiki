import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { SeatClock } from "../src/table/Plaques";
import { Plaques } from "../src/table/Plaques";
import { aCompany, aSeatView, aView } from "./positions";

const NO_CLOCKS: ReadonlyMap<number, SeatClock> = new Map();

describe("Plaques", () => {
    it("shows names, scores, the acting ring, and my marker", () => {
        const company = aCompany([aSeatView(0, { name: "Ala", connected: true }), aSeatView(1)]);
        const view = aView({ to_act: [0], scores: { 0: 12, 1: 7 } });
        const markup = renderToStaticMarkup(
            <Plaques view={view} company={company} mySeat={0} clocks={NO_CLOCKS} clocked={false} />,
        );
        expect(markup).toContain("Ala");
        expect(markup).toContain("Player 2");
        expect(markup).toContain("12");
        expect(markup).toContain('data-acting="true"');
        expect(markup).toContain('data-connected="true"');
        expect(markup).toContain(">you<");
    });

    it("dims unclaimed seats as open", () => {
        const company = aCompany([aSeatView(0, { name: "Ala" }), aSeatView(1, { claimed: false })]);
        const markup = renderToStaticMarkup(
            <Plaques view={aView()} company={company} mySeat={null} clocks={NO_CLOCKS} clocked={false} />,
        );
        expect(markup).toContain("Open seat");
        expect(markup).toContain('data-open="true"');
    });

    it("flags a queued premove", () => {
        const view = aView({ pending_premoves: [1] });
        const markup = renderToStaticMarkup(
            <Plaques view={view} company={aCompany()} mySeat={null} clocks={NO_CLOCKS} clocked={false} />,
        );
        expect(markup).toContain("plaque-premove");
    });

    it("gives every plaque a clock line and counts down on the timed seat", () => {
        const clocks = new Map<number, SeatClock>([[1, { caption: "1:12", urgency: "critical" }]]);
        const markup = renderToStaticMarkup(
            <Plaques view={aView()} company={aCompany()} mySeat={null} clocks={clocks} clocked={true} />,
        );
        expect(markup).toContain("1:12");
        expect(markup).toContain('data-urgency="critical"');
        expect(markup.match(/plaque-clock/g)).toHaveLength(2);
        expect(markup).toContain("—");
    });

    it("leaves the clock line out of an untimed table", () => {
        const markup = renderToStaticMarkup(
            <Plaques view={aView()} company={aCompany()} mySeat={null} clocks={NO_CLOCKS} clocked={false} />,
        );
        expect(markup).not.toContain("plaque-clock");
    });
});
