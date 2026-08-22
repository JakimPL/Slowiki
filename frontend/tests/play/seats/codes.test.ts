import { describe, expect, it } from "vitest";

import type { CodeShape } from "../../../src/play/seats/codes";
import { codeIn, enteredCode, keptCode } from "../../../src/play/seats/codes";

const SHAPE: CodeShape = { alphabet: "ABCDEFGHJKLMNPQRSTUVWXYZ", length: 6 };

describe("codeIn", () => {
    it("reads a bare code in any case, with room around it", () => {
        expect(codeIn("kwpztr", SHAPE)).toBe("KWPZTR");
        expect(codeIn("  KWPZTR \n", SHAPE)).toBe("KWPZTR");
    });

    it("reads the code out of a whole invitation link", () => {
        expect(codeIn("http://192.168.1.5:8000/#code=KWPZTR", SHAPE)).toBe("KWPZTR");
    });

    it("reads the code out of a fragment that carries other fields", () => {
        expect(codeIn("#table=abc123&code=KWPZTR&seat=1", SHAPE)).toBe("KWPZTR");
    });

    it("refuses text that is not a code", () => {
        expect(codeIn("", SHAPE)).toBeNull();
        expect(codeIn("KWPZT", SHAPE)).toBeNull();
        expect(codeIn("KWPZTRX", SHAPE)).toBeNull();
        expect(codeIn("KWPZT1", SHAPE)).toBeNull();
        expect(codeIn("KWPZTI", SHAPE)).toBeNull();
        expect(codeIn("http://192.168.1.5:8000/#table=abc123", SHAPE)).toBeNull();
    });
});

describe("keptCode", () => {
    it("keeps only what the alphabet allows, up to the length", () => {
        expect(keptCode("kw-pz tr", SHAPE)).toBe("KWPZTR");
        expect(keptCode("KWPZTRABC", SHAPE)).toBe("KWPZTR");
        expect(keptCode("0114", SHAPE)).toBe("");
    });
});

describe("enteredCode", () => {
    it("takes a pasted link whole", () => {
        expect(enteredCode("http://192.168.1.5:8000/#code=KWPZTR", SHAPE)).toBe("KWPZTR");
    });

    it("filters what is typed by hand", () => {
        expect(enteredCode("kw", SHAPE)).toBe("KW");
        expect(enteredCode("kw1", SHAPE)).toBe("KW");
    });
});
