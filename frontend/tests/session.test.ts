import { describe, expect, it } from "vitest";

import { fragmentFor, invitationTo, standingIn } from "../src/play/session";

describe("standingIn", () => {
    it("reads table, token, and code from a fragment", () => {
        const standing = standingIn("#table=abc123&token=tok-1&code=KWPZTR");
        expect(standing).toEqual({ table: "abc123", token: "tok-1", code: "KWPZTR" });
    });

    it("treats absent and empty fields as null", () => {
        expect(standingIn("")).toEqual({ table: null, token: null, code: null });
        expect(standingIn("#table=&code=KWPZTR")).toEqual({ table: null, token: null, code: "KWPZTR" });
    });
});

describe("fragmentFor", () => {
    it("writes table and token, leaving an absent code out", () => {
        expect(fragmentFor("abc123", "tok-1", null)).toBe("#table=abc123&token=tok-1");
    });

    it("keeps the shareable code beside the credentials", () => {
        expect(fragmentFor("abc123", "tok-1", "KWPZTR")).toBe("#table=abc123&token=tok-1&code=KWPZTR");
    });

    it("round-trips through standingIn", () => {
        const standing = standingIn(fragmentFor("abc123", "tok-1", "KWPZTR"));
        expect(standing.table).toBe("abc123");
        expect(standing.token).toBe("tok-1");
        expect(standing.code).toBe("KWPZTR");
    });
});

describe("invitationTo", () => {
    it("builds a link carrying the table and the code in the fragment", () => {
        const line = invitationTo("http://192.168.1.5:8000", "/", "abc123", "KWPZTR");
        expect(line).toBe("http://192.168.1.5:8000/#table=abc123&code=KWPZTR");
    });
});
