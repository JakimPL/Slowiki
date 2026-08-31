import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const SHEET = readFileSync(new URL("../../../src/styles.css", import.meta.url), "utf8").replaceAll(
    /\/\*[\s\S]*?\*\//g,
    "",
);

const DECLARATION = /(?:^|[;{}])\s*(?<property>animation[a-z-]*|transition[a-z-]*)\s*:\s*(?<value>[^;{}]*)/g;
const TIME = /(?<![\w-])\d*\.?\d+m?s(?![\w-])/;
const CURVE = /(?<![\w-])(?:linear|ease-in-out|ease-in|ease-out|ease|step-start|step-end|steps|cubic-bezier)(?![\w-])/;
const PACED = new Set(["animation", "transition", "animation-duration", "transition-duration"]);

interface Declaration {
    readonly property: string;
    readonly value: string;
}

function declarations(): readonly Declaration[] {
    return [...SHEET.matchAll(DECLARATION)].map((found) => ({
        property: found.groups?.property ?? "",
        value: (found.groups?.value ?? "").trim(),
    }));
}

describe("the motion vocabulary", () => {
    it("spends a named step at every use site", () => {
        const literal = declarations().filter((held) => TIME.test(held.value));
        expect(literal.map((held) => `${held.property}: ${held.value}`)).toEqual([]);
    });

    it("spends a named curve at every use site", () => {
        const literal = declarations().filter((held) => CURVE.test(held.value));
        expect(literal.map((held) => `${held.property}: ${held.value}`)).toEqual([]);
    });

    it("names a step wherever an effect takes time", () => {
        const paced = declarations().filter((held) => PACED.has(held.property));
        expect(paced.length).toBeGreaterThan(0);
        expect(paced.filter((held) => !held.value.includes("var(--motion-")).map((held) => held.property)).toEqual([]);
    });

    it("stills every effect through one number", () => {
        expect([...SHEET.matchAll(/--motion-scale:\s*0/g)]).toHaveLength(2);
        expect(SHEET).not.toMatch(/--motion-[a-z]+:\s*none/);
    });
});
