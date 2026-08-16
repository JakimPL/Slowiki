import { describe, expect, it } from "vitest";

import type { Watched } from "../src/play/viewing";
import { whileInView } from "../src/play/viewing";

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

describe("whileInView", () => {
    it("holds while visible and releases when hidden", () => {
        const watched = new FakeDocument();
        let holds = 0;
        let releases = 0;
        whileInView(watched, () => {
            holds += 1;
            return () => {
                releases += 1;
            };
        });
        expect(holds).toBe(1);
        watched.turns("hidden");
        expect(releases).toBe(1);
        watched.turns("visible");
        expect(holds).toBe(2);
    });

    it("releases and unsubscribes when stopped", () => {
        const watched = new FakeDocument();
        let releases = 0;
        const stop = whileInView(watched, () => () => {
            releases += 1;
        });
        stop();
        expect(releases).toBe(1);
        watched.turns("hidden");
        watched.turns("visible");
        expect(releases).toBe(1);
    });

    it("waits for visibility before holding", () => {
        const watched = new FakeDocument();
        watched.visibilityState = "hidden";
        let holds = 0;
        whileInView(watched, () => {
            holds += 1;
            return () => {
                return;
            };
        });
        expect(holds).toBe(0);
        watched.turns("visible");
        expect(holds).toBe(1);
    });
});
