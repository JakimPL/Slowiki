import { describe, expect, it } from "vitest";

import { movedOn, reasonOf, refusalOf, Refused, UNKNOWN_CODE } from "../src/api/refusal";
import { aResponse } from "./payloads";

describe("refusalOf", () => {
    it("reads detail and code from an error body", async () => {
        const refused = await refusalOf(aResponse(409, { detail: "not a word", code: "invalid_word" }));
        expect(refused.status).toBe(409);
        expect(refused.message).toBe("not a word");
        expect(refused.code).toBe("invalid_word");
    });

    it("degrades through a body that is not JSON", async () => {
        const refused = await refusalOf(new Response("<html>proxy</html>", { status: 502 }));
        expect(refused.status).toBe(502);
        expect(refused.code).toBe(UNKNOWN_CODE);
    });

    it("degrades through an empty body", async () => {
        const refused = await refusalOf(aResponse(404, null));
        expect(refused.status).toBe(404);
        expect(refused.code).toBe(UNKNOWN_CODE);
    });
});

describe("movedOn", () => {
    it("recognizes the conflict status", () => {
        expect(movedOn(new Refused(409, "stale", "stale_position"))).toBe(true);
        expect(movedOn(new Refused(404, "gone", "unknown_table"))).toBe(false);
    });
});

describe("reasonOf", () => {
    it("keeps a refusal's own sentence", () => {
        expect(reasonOf(new Refused(409, "not your turn", "not_your_turn"))).toBe("not your turn");
    });

    it("turns anything else into a sentence", () => {
        expect(reasonOf(new Error("boom"))).toBe("boom");
        expect(reasonOf("mystery")).toBe("the table could not be reached");
    });
});
