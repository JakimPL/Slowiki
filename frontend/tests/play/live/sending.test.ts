import { describe, expect, it } from "vitest";

import { Refused } from "../../../src/api/refusal";
import { delivered } from "../../../src/play/live/sending";

const STALE = (): Refused => new Refused(409, "position advanced past the submitted sequence", "stale_position");
const ILLEGAL = (): Refused => new Refused(409, "square is occupied", "illegal_move");

interface Recorded {
    readonly bases: number[];
    readonly send: (base: number) => Promise<number>;
}

function sender(...answers: readonly (number | Error)[]): Recorded {
    const bases: number[] = [];
    const queue = [...answers];
    return {
        bases,
        send: (base: number): Promise<number> => {
            bases.push(base);
            const answer = queue.shift();
            if (answer === undefined) {
                throw new Error("sender exhausted");
            }
            return answer instanceof Error ? Promise.reject(answer) : Promise.resolve(answer);
        },
    };
}

describe("delivered", () => {
    it("returns the accepted sequence on a clean answer", async () => {
        const { bases, send } = sender(6);
        await expect(delivered(send, 5, () => Promise.resolve(null))).resolves.toBe(6);
        expect(bases).toEqual([5]);
    });

    it("resends once with the same base when no answer arrived", async () => {
        const { bases, send } = sender(new Error("network down"), 6);
        await expect(delivered(send, 5, () => Promise.resolve(null))).resolves.toBe(6);
        expect(bases).toEqual([5, 5]);
    });

    it("renews the sequence and resubmits after a clean stale refusal", async () => {
        const { bases, send } = sender(STALE(), 8);
        await expect(delivered(send, 5, () => Promise.resolve(7))).resolves.toBe(8);
        expect(bases).toEqual([5, 7]);
    });

    it("keeps the stale refusal when it follows a blind resend", async () => {
        let renewals = 0;
        const { bases, send } = sender(new Error("network down"), STALE());
        const renewed = (): Promise<number | null> => {
            renewals += 1;
            return Promise.resolve(7);
        };
        await expect(delivered(send, 5, renewed)).rejects.toMatchObject({ code: "stale_position" });
        expect(bases).toEqual([5, 5]);
        expect(renewals).toBe(0);
    });

    it("keeps the original stale refusal when renewal fails", async () => {
        const { bases, send } = sender(STALE());
        await expect(delivered(send, 5, () => Promise.resolve(null))).rejects.toMatchObject({
            code: "stale_position",
        });
        expect(bases).toEqual([5]);
    });

    it("propagates other refusals untouched", async () => {
        const { bases, send } = sender(ILLEGAL());
        await expect(delivered(send, 5, () => Promise.resolve(7))).rejects.toMatchObject({ code: "illegal_move" });
        expect(bases).toEqual([5]);
    });

    it("surfaces the refusal answered to the renewed resubmission", async () => {
        const { send } = sender(STALE(), ILLEGAL());
        await expect(delivered(send, 5, () => Promise.resolve(7))).rejects.toMatchObject({ code: "illegal_move" });
    });

    it("keeps renewing through a run of stale refusals", async () => {
        const { bases, send } = sender(STALE(), STALE(), 12);
        let next = 6;
        const renewed = (): Promise<number | null> => Promise.resolve(next++);
        await expect(delivered(send, 5, renewed)).resolves.toBe(12);
        expect(bases).toEqual([5, 6, 7]);
    });

    it("reports a stale refusal that outlasts the retries", async () => {
        const { bases, send } = sender(STALE(), STALE(), STALE(), STALE());
        let next = 6;
        const renewed = (): Promise<number | null> => Promise.resolve(next++);
        await expect(delivered(send, 5, renewed)).rejects.toMatchObject({ code: "stale_position" });
        expect(bases).toEqual([5, 6, 7, 8]);
    });
});
