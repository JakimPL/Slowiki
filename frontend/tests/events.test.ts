import { describe, expect, it } from "vitest";

import { accompanied, advanced, openedFrom, seatedAs } from "../src/play/events";
import { aCompany, anEvent, aSeatView, aTableResponse, aTile, aView } from "./positions";

describe("openedFrom", () => {
    it("keeps the served seq, view, and company", () => {
        const response = aTableResponse({ seq: 4 });
        const state = openedFrom(response);
        expect(state.seq).toBe(4);
        expect(state.view).toBe(response.view);
        expect(state.company).toBe(response.company);
    });
});

describe("advanced", () => {
    it("replaces the view and counts past the event", () => {
        const state = openedFrom(aTableResponse({ seq: 2 }));
        const position = aView({ bag_count: 60 });
        const next = advanced(state, anEvent({ seq: 2, position }));
        expect(next.seq).toBe(3);
        expect(next.view).toBe(position);
        expect(next.company).toBe(state.company);
    });

    it("ignores replayed events from before the current view", () => {
        const state = openedFrom(aTableResponse({ seq: 5 }));
        const next = advanced(state, anEvent({ seq: 3 }));
        expect(next).toBe(state);
    });

    it("accepts a gap because every event carries a whole snapshot", () => {
        const state = openedFrom(aTableResponse({ seq: 1 }));
        const next = advanced(state, anEvent({ seq: 7 }));
        expect(next.seq).toBe(8);
    });
});

describe("accompanied", () => {
    it("replaces only the company", () => {
        const state = openedFrom(aTableResponse());
        const company = aCompany([aSeatView(0, { connected: true })]);
        const next = accompanied(state, company);
        expect(next.company).toBe(company);
        expect(next.view).toBe(state.view);
        expect(next.seq).toBe(state.seq);
    });
});

describe("seatedAs", () => {
    it("finds the seat whose rack is visible", () => {
        expect(seatedAs(aView({ racks: { 0: null, 1: [aTile()] } }))).toBe(1);
    });

    it("treats an empty visible rack as a seat", () => {
        expect(seatedAs(aView({ racks: { 3: [] } }))).toBe(3);
    });

    it("returns null for a spectator", () => {
        expect(seatedAs(aView({ racks: { 0: null, 1: null } }))).toBeNull();
    });
});
