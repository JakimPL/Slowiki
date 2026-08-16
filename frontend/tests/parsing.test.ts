import { describe, expect, it } from "vitest";

import { bodyOf, parsed } from "../src/api/parsing";
import { aResponse } from "./payloads";

describe("bodyOf", () => {
    it("parses typed JSON text", () => {
        expect(bodyOf<{ seq: number }>('{"seq": 4}')).toEqual({ seq: 4 });
    });
});

describe("parsed", () => {
    it("parses a response body", async () => {
        await expect(parsed<{ seq: number }>(aResponse(200, { seq: 2 }))).resolves.toEqual({ seq: 2 });
    });
});
