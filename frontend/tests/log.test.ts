import { describe, expect, it } from "vitest";

import { advanced, openedFrom } from "../src/play/events";
import { appendedLog, LOG_LIMIT, logEntryOf } from "../src/play/log";
import { anEvent, aPlayRecord, aTableResponse, aView } from "./positions";

describe("logEntryOf", () => {
    it("reads a play from the changed last-play figures", () => {
        const before = aView();
        const event = anEvent({
            seq: 3,
            actor: 1,
            position: aView({
                last_play: aPlayRecord({ player: 1, points: 34, words: [{ text: "WÓZ", points: 34 }] }),
            }),
        });
        expect(logEntryOf(event, before)).toEqual({
            seq: 3,
            actor: 1,
            kind: "play",
            words: [{ text: "WÓZ", points: 34 }],
            points: 34,
            reason: null,
        });
    });

    it("keeps an unchanged last play out of the log", () => {
        const record = aPlayRecord();
        const before = aView({ last_play: record });
        const event = anEvent({ position: aView({ last_play: record, consecutive_passes: 1 }), actor: 1 });
        expect(logEntryOf(event, before)?.kind).toBe("pass");
    });

    it("classifies exchanges and passes by the served counters", () => {
        const before = aView();
        const exchanged = anEvent({ actor: 0, position: aView({ exchange_counts: { 0: 1, 1: 0 } }) });
        expect(logEntryOf(exchanged, before)?.kind).toBe("exchange");
        const passed = anEvent({ actor: 0, position: aView({ consecutive_passes: 1 }) });
        expect(logEntryOf(passed, before)?.kind).toBe("pass");
    });

    it("keeps reorders and premove bookkeeping out of the log", () => {
        const before = aView();
        expect(logEntryOf(anEvent({ position: aView() }), before)).toBeNull();
        expect(logEntryOf(anEvent({ kind: "premove_set" }), before)).toBeNull();
        expect(logEntryOf(anEvent({ kind: "premove_cleared" }), before)).toBeNull();
    });

    it("surfaces a discarded premove with its reason", () => {
        const entry = logEntryOf(anEvent({ kind: "premove_discarded", actor: 1, reason: "not_your_turn" }), aView());
        expect(entry).toEqual({
            seq: 0,
            actor: 1,
            kind: "premove-returned",
            words: [],
            points: null,
            reason: "not_your_turn",
        });
    });
});

describe("appendedLog", () => {
    it("caps the kept entries", () => {
        const full = Array.from({ length: LOG_LIMIT }, (_, at) => ({
            seq: at,
            actor: 0,
            kind: "pass" as const,
            words: [],
            points: null,
            reason: null,
        }));
        const grown = appendedLog(full, { seq: 99, actor: 0, kind: "pass", words: [], points: null, reason: null });
        expect(grown).toHaveLength(LOG_LIMIT);
        expect(grown.at(-1)?.seq).toBe(99);
        expect(appendedLog(full, null)).toBe(full);
    });
});

describe("advanced folds the log", () => {
    it("collects entries as events land", () => {
        const state = openedFrom(aTableResponse());
        const played = advanced(state, anEvent({ seq: 0, actor: 0, position: aView({ last_play: aPlayRecord() }) }));
        expect(played.log).toHaveLength(1);
        const passed = advanced(
            played,
            anEvent({ seq: 1, actor: 1, position: aView({ last_play: aPlayRecord(), consecutive_passes: 1 }) }),
        );
        expect(passed.log.map((entry) => entry.kind)).toEqual(["play", "pass"]);
    });
});
