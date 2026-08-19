import type { FetchEventSourceInit } from "@microsoft/fetch-event-source";
import { describe, expect, it } from "vitest";

import type { Streamed } from "../../src/api/streaming";
import { CLOCK_EVENT, follow, LAST_EVENT_ID_HEADER, PRESENCE_EVENT } from "../../src/api/streaming";
import type { ClockView, CompanyView, EventView } from "../../src/api/views";

interface Recorded {
    url: string;
    init: FetchEventSourceInit;
}

function aTransport(recorded: Recorded[]): (url: string, init: FetchEventSourceInit) => Promise<void> {
    return (url, init) => {
        recorded.push({ url, init });
        return new Promise(() => {
            return;
        });
    };
}

function aStreamed(
    commits: EventView[],
    companies: CompanyView[],
    drops: string[],
    clocks: ClockView[] = [],
): Streamed {
    return {
        onOpen: () => {
            return;
        },
        onCommit: (event) => {
            commits.push(event);
        },
        onPresence: (company) => {
            companies.push(company);
        },
        onClock: (clock) => {
            clocks.push(clock);
        },
        onDropped: (reason) => {
            drops.push(reason);
        },
    };
}

describe("follow", () => {
    it("resumes with a Last-Event-ID header when starting past zero", () => {
        const recorded: Recorded[] = [];
        follow(aTransport(recorded), "/tables/t/events", { "X-Seat-Token": "tok" }, 5, aStreamed([], [], []));
        expect(recorded[0]?.init.headers).toEqual({ "X-Seat-Token": "tok", [LAST_EVENT_ID_HEADER]: "4" });
    });

    it("sends bare headers when starting from zero", () => {
        const recorded: Recorded[] = [];
        follow(aTransport(recorded), "/tables/t/events", { "X-Seat-Token": "tok" }, 0, aStreamed([], [], []));
        expect(recorded[0]?.init.headers).toEqual({ "X-Seat-Token": "tok" });
    });

    it("dispatches presence and clock frames apart from commits", () => {
        const recorded: Recorded[] = [];
        const commits: EventView[] = [];
        const companies: CompanyView[] = [];
        const clocks: ClockView[] = [];
        follow(aTransport(recorded), "/tables/t/events", {}, 0, aStreamed(commits, companies, [], clocks));
        const handle = recorded[0]?.init.onmessage;
        expect(handle).toBeDefined();
        handle?.({
            id: "",
            event: PRESENCE_EVENT,
            data: JSON.stringify({ seats: [] }),
        });
        handle?.({
            id: "",
            event: CLOCK_EVENT,
            data: JSON.stringify({ server_time: 1000, deadline: 1090, seat: 0, per_turn_seconds: 90 }),
        });
        handle?.({
            id: "0",
            event: "",
            data: JSON.stringify({ seq: 0, kind: "move", actor: 0, move: null, reason: null, position: {} }),
        });
        handle?.({ id: "", event: "", data: "" });
        expect(companies).toHaveLength(1);
        expect(clocks).toHaveLength(1);
        expect(clocks[0]?.deadline).toBe(1090);
        expect(commits).toHaveLength(1);
        expect(commits[0]?.seq).toBe(0);
    });

    it("stops following when released", () => {
        const recorded: Recorded[] = [];
        const release = follow(aTransport(recorded), "/tables/t/events", {}, 0, aStreamed([], [], []));
        release();
        expect(recorded[0]?.init.signal?.aborted).toBe(true);
    });
});
