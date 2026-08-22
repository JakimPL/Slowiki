import { describe, expect, it } from "vitest";

import { fragmentFor, invitationTo, standingIn, withoutFragment } from "../../../src/play/seats/session";

describe("standingIn", () => {
    it("reads table, token, code, and seat from a fragment", () => {
        const standing = standingIn("#table=abc123&token=tok-1&code=KWPZTR&seat=1");
        expect(standing).toEqual({ table: "abc123", token: "tok-1", code: "KWPZTR", seated: 1 });
    });

    it("treats absent and empty fields as null", () => {
        expect(standingIn("")).toEqual({ table: null, token: null, code: null, seated: null });
        expect(standingIn("#table=&code=KWPZTR")).toEqual({
            table: null,
            token: null,
            code: "KWPZTR",
            seated: null,
        });
    });

    it("rejects a malformed seat field", () => {
        expect(standingIn("#table=abc&token=tok&seat=abc").seated).toBeNull();
        expect(standingIn("#table=abc&token=tok&seat=-2").seated).toBeNull();
    });
});

describe("fragmentFor", () => {
    it("writes table, token, and seat, leaving an absent code out", () => {
        expect(fragmentFor("abc123", "tok-1", null, 0)).toBe("#table=abc123&token=tok-1&seat=0");
    });

    it("keeps the shareable code beside the credentials", () => {
        expect(fragmentFor("abc123", "tok-1", "KWPZTR", 1)).toBe("#table=abc123&token=tok-1&code=KWPZTR&seat=1");
    });

    it("round-trips through standingIn", () => {
        const standing = standingIn(fragmentFor("abc123", "tok-1", "KWPZTR", 1));
        expect(standing.table).toBe("abc123");
        expect(standing.token).toBe("tok-1");
        expect(standing.code).toBe("KWPZTR");
        expect(standing.seated).toBe(1);
    });
});

describe("withoutFragment", () => {
    it("drops the seat from an address, keeping path and query", () => {
        expect(withoutFragment("http://host/?pass=3#table=abc123&token=tok-1&seat=1")).toBe("http://host/?pass=3");
    });

    it("leaves an address that carries no fragment alone", () => {
        expect(withoutFragment("http://host/play")).toBe("http://host/play");
    });
});

describe("invitationTo", () => {
    it("builds a link carrying the join code alone", () => {
        const line = invitationTo("http://192.168.1.5:8000", "/", "KWPZTR");
        expect(line).toBe("http://192.168.1.5:8000/#code=KWPZTR");
    });
});
