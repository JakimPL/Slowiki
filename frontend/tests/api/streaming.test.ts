import type { FetchEventSourceInit } from "@microsoft/fetch-event-source";
import { describe, expect, it } from "vitest";

import { GONE_STATUS, Refused } from "../../src/api/refusal";
import type { Streamed } from "../../src/api/streaming";
import {
    CLOCK_EVENT,
    follow,
    HEARTBEAT_EVENT,
    LAST_EVENT_ID_HEADER,
    POSITION_EVENT,
    PRESENCE_EVENT,
    RETRY_AFTER_DROP_MILLISECONDS,
} from "../../src/api/streaming";
import type { ClockView, CompanyView, EventView, PositionView } from "../../src/api/views";

interface Recorded {
    url: string;
    init: FetchEventSourceInit;
}

interface Heard {
    beats: number;
    readonly commits: EventView[];
    readonly companies: CompanyView[];
    readonly positions: PositionView[];
    readonly clocks: ClockView[];
    readonly drops: string[];
    readonly departures: string[];
    ends: number;
}

function aTransport(recorded: Recorded[]): (url: string, init: FetchEventSourceInit) => Promise<void> {
    return (url, init) => {
        recorded.push({ url, init });
        return new Promise(() => {
            return;
        });
    };
}

function aFailingTransport(
    recorded: Recorded[],
    trouble: Refused,
): (url: string, init: FetchEventSourceInit) => Promise<void> {
    return (url, init) => {
        recorded.push({ url, init });
        return Promise.reject(trouble);
    };
}

function aResumingTransport(
    recorded: Recorded[],
    id: string,
): (url: string, init: FetchEventSourceInit) => Promise<void> {
    return (url, init) => {
        const headers = { ...init.headers, "last-event-id": id };
        recorded.push({ url, init: { ...init, headers } });
        return new Promise(() => {
            return;
        });
    };
}

function aListener(): { heard: Heard; streamed: Streamed } {
    const heard: Heard = {
        beats: 0,
        commits: [],
        companies: [],
        positions: [],
        clocks: [],
        drops: [],
        departures: [],
        ends: 0,
    };
    return {
        heard,
        streamed: {
            onOpen: () => {
                return;
            },
            onBeat: () => {
                heard.beats += 1;
            },
            onCommit: (event) => {
                heard.commits.push(event);
            },
            onPresence: (company) => {
                heard.companies.push(company);
            },
            onPosition: (view) => {
                heard.positions.push(view);
            },
            onClock: (clock) => {
                heard.clocks.push(clock);
            },
            onDropped: (reason) => {
                heard.drops.push(reason);
            },
            onEnded: () => {
                heard.ends += 1;
            },
            onGone: (reason) => {
                heard.departures.push(reason);
            },
        },
    };
}

describe("follow", () => {
    it("resumes with a Last-Event-ID header when starting past zero", () => {
        const recorded: Recorded[] = [];
        follow(aTransport(recorded), "/tables/t/events", { "X-Seat-Token": "tok" }, 5, aListener().streamed);
        expect(recorded[0]?.init.headers).toEqual({ "X-Seat-Token": "tok", [LAST_EVENT_ID_HEADER]: "4" });
    });

    it("leaves the transport one resume header to overwrite", () => {
        const recorded: Recorded[] = [];
        follow(aResumingTransport(recorded, "32"), "/tables/t/events", {}, 22, aListener().streamed);
        const sent = recorded[0]?.init.headers ?? {};
        expect(Object.keys(sent).filter((key) => key.toLowerCase() === "last-event-id")).toEqual(["last-event-id"]);
        expect(sent["last-event-id"]).toBe("32");
    });

    it("sends bare headers when starting from zero", () => {
        const recorded: Recorded[] = [];
        follow(aTransport(recorded), "/tables/t/events", { "X-Seat-Token": "tok" }, 0, aListener().streamed);
        expect(recorded[0]?.init.headers).toEqual({ "X-Seat-Token": "tok" });
    });

    it("dispatches presence, position and clock frames apart from commits", () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        follow(aTransport(recorded), "/tables/t/events", {}, 0, streamed);
        const handle = recorded[0]?.init.onmessage;
        expect(handle).toBeDefined();
        handle?.({
            id: "",
            event: PRESENCE_EVENT,
            data: JSON.stringify({ seats: [] }),
        });
        handle?.({
            id: "",
            event: POSITION_EVENT,
            data: JSON.stringify({ bag_count: 60, racks: { 0: [] } }),
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
        expect(heard.companies).toHaveLength(1);
        expect(heard.positions).toHaveLength(1);
        expect(heard.positions[0]?.bag_count).toBe(60);
        expect(heard.clocks).toHaveLength(1);
        expect(heard.clocks[0]?.deadline).toBe(1090);
        expect(heard.commits).toHaveLength(1);
        expect(heard.commits[0]?.seq).toBe(0);
    });

    it("counts a heartbeat as liveness and nothing else", () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        follow(aTransport(recorded), "/tables/t/events", {}, 0, streamed);
        const handle = recorded[0]?.init.onmessage;
        handle?.({ id: "", event: HEARTBEAT_EVENT, data: JSON.stringify({ server_time: 1000 }) });
        expect(heard.beats).toBe(1);
        expect(heard.commits).toHaveLength(0);
        expect(heard.companies).toHaveLength(0);
        expect(heard.positions).toHaveLength(0);
        expect(heard.clocks).toHaveLength(0);
    });

    it("counts every frame as liveness", () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        follow(aTransport(recorded), "/tables/t/events", {}, 0, streamed);
        const handle = recorded[0]?.init.onmessage;
        handle?.({ id: "", event: PRESENCE_EVENT, data: JSON.stringify({ seats: [] }) });
        handle?.({ id: "", event: HEARTBEAT_EVENT, data: JSON.stringify({ server_time: 1 }) });
        expect(heard.beats).toBe(2);
    });

    it("keeps retrying a connection that merely dropped", () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        follow(aTransport(recorded), "/tables/t/events", {}, 0, streamed);
        const trouble = recorded[0]?.init.onerror;
        expect(trouble?.(new Error("network down"))).toBe(RETRY_AFTER_DROP_MILLISECONDS);
        expect(heard.drops).toEqual(["network down"]);
        expect(heard.departures).toEqual([]);
    });

    it("gives up on a table the server no longer holds", async () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        const closed = new Refused(GONE_STATUS, "the table has closed", "table_closed");
        follow(aFailingTransport(recorded, closed), "/tables/t/events", {}, 0, streamed);
        const trouble = recorded[0]?.init.onerror;
        expect(() => trouble?.(closed)).toThrow(closed);
        await Promise.resolve();
        expect(heard.departures).toEqual(["the table has closed"]);
        expect(heard.drops).toEqual([]);
    });

    it("follows again when the table ends the stream", () => {
        const recorded: Recorded[] = [];
        const { heard, streamed } = aListener();
        follow(aTransport(recorded), "/tables/t/events", {}, 0, streamed);
        recorded[0]?.init.onclose?.();
        expect(heard.ends).toBe(1);
    });

    it("stops following when released", () => {
        const recorded: Recorded[] = [];
        const release = follow(aTransport(recorded), "/tables/t/events", {}, 0, aListener().streamed);
        release();
        expect(recorded[0]?.init.signal?.aborted).toBe(true);
    });
});
