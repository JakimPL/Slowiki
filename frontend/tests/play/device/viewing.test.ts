import { describe, expect, it } from "vitest";

import type { Watched } from "../../../src/play/device/viewing";
import { whenInView } from "../../../src/play/device/viewing";

class FakeDocument implements Watched {
    visibilityState: DocumentVisibilityState = "visible";
    private listeners: (() => void)[] = [];

    addEventListener(_type: "visibilitychange", listener: () => void): void {
        this.listeners.push(listener);
    }

    removeEventListener(_type: "visibilitychange", listener: () => void): void {
        this.listeners = this.listeners.filter((held) => held !== listener);
    }

    turns(state: DocumentVisibilityState): void {
        this.visibilityState = state;
        for (const listener of [...this.listeners]) {
            listener();
        }
    }
}

describe("whenInView", () => {
    it("calls back each time the page comes back into view", () => {
        const watched = new FakeDocument();
        let returns = 0;
        whenInView(watched, () => {
            returns += 1;
        });
        expect(returns).toBe(0);
        watched.turns("hidden");
        expect(returns).toBe(0);
        watched.turns("visible");
        expect(returns).toBe(1);
        watched.turns("hidden");
        watched.turns("visible");
        expect(returns).toBe(2);
    });

    it("unsubscribes when stopped", () => {
        const watched = new FakeDocument();
        let returns = 0;
        const stop = whenInView(watched, () => {
            returns += 1;
        });
        stop();
        watched.turns("hidden");
        watched.turns("visible");
        expect(returns).toBe(0);
    });
});
