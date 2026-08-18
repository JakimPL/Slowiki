import { describe, expect, it } from "vitest";

import type { InflectedForm, Inflection, LoreReading, Part } from "../src/api/lore";
import type { Paradigm, ParadigmGrid } from "../src/play/paradigm";
import { paradigmOf } from "../src/play/paradigm";
import { DIMENSION_ORDER, termsOn } from "../src/play/tagset";
import { aForm, aReading, someInflection } from "./lore";

function form(text: string, tags: Partial<Inflection>): InflectedForm {
    return aForm({ text, tags: someInflection(tags) });
}

function readingOf(part: Part, forms: readonly InflectedForm[]): LoreReading {
    return aReading({ part, forms });
}

const PIŁA: readonly InflectedForm[] = [
    form("PIŁA", { cases: ["mianownik"], number: "pojedyncza", genders: ["żeński"] }),
    form("PIŁY", { cases: ["dopełniacz"], number: "pojedyncza", genders: ["żeński"] }),
    form("PILE", { cases: ["celownik", "miejscownik"], number: "pojedyncza", genders: ["żeński"] }),
    form("PIŁĘ", { cases: ["biernik"], number: "pojedyncza", genders: ["żeński"] }),
    form("PIŁĄ", { cases: ["narzędnik"], number: "pojedyncza", genders: ["żeński"] }),
    form("PIŁO", { cases: ["wołacz"], number: "pojedyncza", genders: ["żeński"] }),
    form("PIŁY", { cases: ["mianownik", "biernik", "wołacz"], number: "mnoga", genders: ["żeński"] }),
    form("PIŁ", { cases: ["dopełniacz"], number: "mnoga", genders: ["żeński"] }),
    form("PIŁOM", { cases: ["celownik"], number: "mnoga", genders: ["żeński"] }),
    form("PIŁAMI", { cases: ["narzędnik"], number: "mnoga", genders: ["żeński"] }),
    form("PIŁACH", { cases: ["miejscownik"], number: "mnoga", genders: ["żeński"] }),
];

const DRZWI: readonly InflectedForm[] = [
    form("DRZWI", { cases: ["mianownik", "biernik", "wołacz"], number: "mnoga", genders: ["nijaki"] }),
    form("DRZWI", { cases: ["dopełniacz"], number: "mnoga", genders: ["nijaki"] }),
    form("DRZWIOM", { cases: ["celownik"], number: "mnoga", genders: ["nijaki"] }),
    form("DRZWIAMI", { cases: ["narzędnik"], number: "mnoga", genders: ["nijaki"] }),
    form("DRZWIACH", { cases: ["miejscownik"], number: "mnoga", genders: ["nijaki"] }),
];

const PROFESOR: readonly InflectedForm[] = [
    form("PROFESOR", { cases: ["mianownik"], number: "pojedyncza", genders: ["męskoosobowy"] }),
    form("PROFESOROWIE", { cases: ["mianownik"], number: "mnoga", genders: ["męskoosobowy"] }),
    form("PROFESORY", {
        cases: ["mianownik"],
        number: "mnoga",
        genders: ["męskoosobowy"],
        deprecative: true,
    }),
];

const DOBRY: readonly InflectedForm[] = [
    form("DOBRY", { cases: ["mianownik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "równy" }),
    form("DOBRA", { cases: ["mianownik"], number: "pojedyncza", genders: ["żeński"], degree: "równy" }),
    form("DOBREJ", { cases: ["dopełniacz"], number: "pojedyncza", genders: ["żeński"], degree: "równy" }),
    form("DOBRZY", { cases: ["mianownik"], number: "mnoga", genders: ["męskoosobowy"], degree: "równy" }),
    form("LEPSZY", { cases: ["mianownik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "wyższy" }),
];

const SZYBKO: readonly InflectedForm[] = [
    form("SZYBKO", { degree: "równy" }),
    form("SZYBCIEJ", { degree: "wyższy" }),
    form("NAJSZYBCIEJ", { degree: "najwyższy" }),
];

const PISAĆ: readonly InflectedForm[] = [
    form("PISAĆ", { verb_form: "bezokolicznik", aspects: ["niedokonany"] }),
    form("PISZĘ", {
        verb_form: "forma osobowa",
        mood: "oznajmujący",
        tense: "teraźniejszy",
        person: "pierwsza",
        number: "pojedyncza",
        aspects: ["niedokonany"],
    }),
    form("PISZESZ", {
        verb_form: "forma osobowa",
        mood: "oznajmujący",
        tense: "teraźniejszy",
        person: "druga",
        number: "pojedyncza",
        aspects: ["niedokonany"],
    }),
    form("PISZEMY", {
        verb_form: "forma osobowa",
        mood: "oznajmujący",
        tense: "teraźniejszy",
        person: "pierwsza",
        number: "mnoga",
        aspects: ["niedokonany"],
    }),
    form("PISAŁ", {
        verb_form: "forma przeszła",
        mood: "oznajmujący",
        tense: "przeszły",
        number: "pojedyncza",
        genders: ["męskoosobowy", "męskozwierzęcy", "męskorzeczowy"],
        aspects: ["niedokonany"],
    }),
    form("PISAŁA", {
        verb_form: "forma przeszła",
        mood: "oznajmujący",
        tense: "przeszły",
        number: "pojedyncza",
        genders: ["żeński"],
        aspects: ["niedokonany"],
    }),
    form("PISALI", {
        verb_form: "forma przeszła",
        mood: "oznajmujący",
        tense: "przeszły",
        number: "mnoga",
        genders: ["męskoosobowy"],
        aspects: ["niedokonany"],
    }),
    form("PISANY", {
        verb_form: "imiesłów bierny",
        cases: ["mianownik"],
        number: "pojedyncza",
        genders: ["męskorzeczowy"],
        negation: false,
        aspects: ["niedokonany"],
    }),
    form("NIEPISANY", {
        verb_form: "imiesłów bierny",
        cases: ["mianownik"],
        number: "pojedyncza",
        genders: ["męskorzeczowy"],
        negation: true,
        aspects: ["niedokonany"],
    }),
    form("PISZĄC", { verb_form: "imiesłów współczesny", aspects: ["niedokonany"] }),
    form("PISANIE", {
        verb_form: "odsłownik",
        cases: ["mianownik"],
        number: "pojedyncza",
        genders: ["nijaki"],
        aspects: ["niedokonany"],
    }),
];

function textsIn(paradigm: Paradigm): readonly string[] {
    const gridded = paradigm.grids.flatMap((grid) =>
        grid.rows.flatMap((row) => row.cells.flatMap((cell) => cell.forms.map((placed) => placed.text))),
    );
    const listed = paradigm.lists.flatMap((list) => list.forms.map((placed) => placed.text));
    return [...gridded, ...listed, ...paradigm.rest.map((placed) => placed.text)];
}

function shownTermsFor(paradigm: Paradigm, text: string): readonly string[] {
    const shown = new Set(paradigm.heading);
    for (const list of paradigm.lists) {
        if (list.forms.some((placed) => placed.text === text)) {
            list.titles.forEach((title) => shown.add(title));
        }
    }
    for (const grid of paradigm.grids) {
        const columns = grid.columns;
        for (const row of grid.rows) {
            row.cells.forEach((cell, index) => {
                if (!cell.forms.some((placed) => placed.text === text)) {
                    return;
                }
                grid.titles.forEach((title) => shown.add(title));
                shown.add(row.term);
                const columnTerm = columns?.terms[index];
                if (columnTerm !== undefined) {
                    shown.add(columnTerm);
                }
            });
        }
    }
    return [...shown];
}

function cellTextsIn(grid: ParadigmGrid | undefined, rowTerm: string, column: number): readonly string[] {
    const row = grid?.rows.find((one) => one.term === rowTerm);
    return row?.cells[column]?.forms.map((placed) => placed.text) ?? [];
}

function rotated(forms: readonly InflectedForm[]): readonly InflectedForm[] {
    return [...forms.slice(3), ...forms.slice(0, 3)];
}

const SINGULAR = 0;

const PLURAL = 1;

describe("paradigmOf invariants", () => {
    it("places every form of a whole verb family somewhere", () => {
        const placed = textsIn(paradigmOf(readingOf("czasownik", PISAĆ)));
        for (const one of PISAĆ) {
            expect(placed, one.text).toContain(one.text);
        }
    });

    it("holds a form only in cells whose row and column terms it carries", () => {
        for (const grid of paradigmOf(readingOf("czasownik", PISAĆ)).grids) {
            const columns = grid.columns;
            for (const row of grid.rows) {
                expect(row.cells).toHaveLength(columns === null ? 1 : columns.terms.length);
                row.cells.forEach((cell, index) => {
                    for (const placed of cell.forms) {
                        expect(termsOn(placed.tags, grid.rowDimension)).toContain(row.term);
                        if (columns !== null) {
                            expect(termsOn(placed.tags, columns.dimension)).toContain(columns.terms[index]);
                        }
                    }
                });
            }
        }
    });

    it("shows every term a form carries in its heading, its titles or its axes", () => {
        const paradigm = paradigmOf(readingOf("czasownik", PISAĆ));
        for (const one of PISAĆ) {
            const shown = shownTermsFor(paradigm, one.text);
            for (const dimension of DIMENSION_ORDER) {
                for (const term of termsOn(one.tags, dimension)) {
                    expect(shown, `${one.text} · ${term}`).toContain(term);
                }
            }
        }
    });

    it("lays out shuffled forms identically", () => {
        const straight = paradigmOf(readingOf("czasownik", PISAĆ));
        expect(paradigmOf(readingOf("czasownik", [...PISAĆ].reverse()))).toEqual(straight);
        expect(paradigmOf(readingOf("czasownik", rotated(PISAĆ)))).toEqual(straight);
    });
});

describe("paradigmOf for a noun", () => {
    it("reads the paradigm as cases by number under a gender heading", () => {
        const paradigm = paradigmOf(readingOf("rzeczownik", PIŁA));
        expect(paradigm.heading).toEqual(["żeński"]);
        expect(paradigm.grids).toHaveLength(1);
        expect(paradigm.lists).toEqual([]);
        expect(paradigm.rest).toEqual([]);
        const grid = paradigm.grids[0];
        expect(grid?.titles).toEqual([]);
        expect(grid?.rowDimension).toBe("case");
        expect(grid?.columns).toEqual({ dimension: "number", terms: ["pojedyncza", "mnoga"] });
        expect(grid?.rows.map((row) => row.term)).toEqual([
            "mianownik",
            "dopełniacz",
            "celownik",
            "biernik",
            "narzędnik",
            "miejscownik",
            "wołacz",
        ]);
    });

    it("stands a syncretic form in every row and column its terms name", () => {
        const grid = paradigmOf(readingOf("rzeczownik", PIŁA)).grids[0];
        expect(cellTextsIn(grid, "celownik", SINGULAR)).toEqual(["PILE"]);
        expect(cellTextsIn(grid, "miejscownik", SINGULAR)).toEqual(["PILE"]);
        expect(cellTextsIn(grid, "mianownik", PLURAL)).toEqual(["PIŁY"]);
        expect(cellTextsIn(grid, "biernik", PLURAL)).toEqual(["PIŁY"]);
        expect(cellTextsIn(grid, "wołacz", PLURAL)).toEqual(["PIŁY"]);
    });

    it("gives a plurale tantum a single column", () => {
        const grid = paradigmOf(readingOf("rzeczownik", DRZWI)).grids[0];
        expect(grid?.columns).toEqual({ dimension: "number", terms: ["mnoga"] });
        expect(grid?.rows.every((row) => row.cells.length === 1)).toBe(true);
    });

    it("takes the deprecative forms into a grid of their own", () => {
        const paradigm = paradigmOf(readingOf("rzeczownik", PROFESOR));
        expect(paradigm.heading).toEqual(["męskoosobowy"]);
        expect(paradigm.grids.map((grid) => grid.titles)).toEqual([[], ["deprecjatywny"]]);
        expect(textsIn(paradigm)).toEqual(["PROFESOR", "PROFESOROWIE", "PROFESORY"]);
    });
});

describe("paradigmOf for an adjective", () => {
    it("reads cases by gender in a grid per number and degree", () => {
        const paradigm = paradigmOf(readingOf("przymiotnik", DOBRY));
        expect(paradigm.heading).toEqual([]);
        expect(paradigm.grids.map((grid) => grid.titles)).toEqual([
            ["pojedyncza", "równy"],
            ["pojedyncza", "wyższy"],
            ["mnoga", "równy"],
        ]);
        const leading = paradigm.grids[0];
        expect(leading?.rowDimension).toBe("case");
        expect(leading?.columns).toEqual({ dimension: "gender", terms: ["męskoosobowy", "żeński"] });
        expect(leading?.rows.map((row) => row.term)).toEqual(["mianownik", "dopełniacz"]);
    });
});

describe("paradigmOf for an adverb", () => {
    it("reads the degrees as rows of one unnamed column", () => {
        const paradigm = paradigmOf(readingOf("przysłówek", SZYBKO));
        expect(paradigm.grids).toHaveLength(1);
        const grid = paradigm.grids[0];
        expect(grid?.rowDimension).toBe("degree");
        expect(grid?.columns).toBeNull();
        expect(grid?.rows.map((row) => row.term)).toEqual(["równy", "wyższy", "najwyższy"]);
        expect(grid?.rows.map((row) => row.cells.flatMap((cell) => cell.forms.map((placed) => placed.text)))).toEqual([
            ["SZYBKO"],
            ["SZYBCIEJ"],
            ["NAJSZYBCIEJ"],
        ]);
    });
});

describe("paradigmOf for a verb", () => {
    it("names the aspect once and every verb form in its own block", () => {
        const paradigm = paradigmOf(readingOf("czasownik", PISAĆ));
        expect(paradigm.heading).toEqual(["niedokonany"]);
        expect(paradigm.lists.map((list) => list.titles)).toEqual([["bezokolicznik"], ["imiesłów współczesny"]]);
        expect(paradigm.grids.map((grid) => grid.titles)).toEqual([
            ["forma osobowa", "oznajmujący", "teraźniejszy"],
            ["forma przeszła", "oznajmujący", "przeszły"],
            ["imiesłów bierny", "pojedyncza"],
            ["imiesłów bierny", "pojedyncza", "zaprzeczony"],
            ["odsłownik", "nijaki"],
        ]);
        expect(paradigm.rest).toEqual([]);
    });

    it("reads the present tense as persons by number", () => {
        const grid = paradigmOf(readingOf("czasownik", PISAĆ)).grids[0];
        expect(grid?.rowDimension).toBe("person");
        expect(grid?.columns).toEqual({ dimension: "number", terms: ["pojedyncza", "mnoga"] });
        expect(grid?.rows.map((row) => row.cells.flatMap((cell) => cell.forms.map((placed) => placed.text)))).toEqual([
            ["PISZĘ", "PISZEMY"],
            ["PISZESZ"],
        ]);
    });

    it("reads the past tense as genders by number", () => {
        const grid = paradigmOf(readingOf("czasownik", PISAĆ)).grids[1];
        expect(grid?.rowDimension).toBe("gender");
        expect(grid?.rows.map((row) => row.term)).toEqual([
            "męskoosobowy",
            "męskozwierzęcy",
            "męskorzeczowy",
            "żeński",
        ]);
        expect(grid?.rows[0]?.cells.map((cell) => cell.forms.map((placed) => placed.text))).toEqual([
            ["PISAŁ"],
            ["PISALI"],
        ]);
    });

    it("keeps the infinitive as a list of its own", () => {
        const list = paradigmOf(readingOf("czasownik", PISAĆ)).lists[0];
        expect(list?.forms.map((placed) => placed.text)).toEqual(["PISAĆ"]);
    });
});

describe("paradigmOf for the parts that never inflect", () => {
    it("reads a preposition as one list without titles", () => {
        const paradigm = paradigmOf(readingOf("przyimek", [form("W", {}), form("WE", {})]));
        expect(paradigm.grids).toEqual([]);
        expect(paradigm.rest).toEqual([]);
        expect(paradigm.lists.map((list) => list.titles)).toEqual([[]]);
        expect(paradigm.lists[0]?.forms.map((placed) => placed.text)).toEqual(["W", "WE"]);
    });
});

describe("paradigmOf at the edges", () => {
    it("reads a reading without forms as an empty paradigm", () => {
        expect(paradigmOf(readingOf("rzeczownik", []))).toEqual({ heading: [], grids: [], lists: [], rest: [] });
    });

    it("keeps a form no axis can hold in the rest", () => {
        const paradigm = paradigmOf(
            readingOf("rzeczownik", [
                form("KOT", { cases: ["mianownik"], number: "pojedyncza", genders: ["męskozwierzęcy"] }),
                form("KOCIE", { genders: ["męskozwierzęcy"] }),
            ]),
        );
        expect(paradigm.rest.map((placed) => placed.text)).toEqual(["KOCIE"]);
        expect(textsIn(paradigm)).toEqual(["KOT", "KOCIE"]);
    });

    it("drops a form repeated in the same cell to one entry", () => {
        const twice = form("KOT", { cases: ["mianownik"], number: "pojedyncza", genders: ["męskozwierzęcy"] });
        const grid = paradigmOf(readingOf("rzeczownik", [twice, twice])).grids[0];
        expect(grid?.rows[0]?.cells[0]?.forms).toHaveLength(1);
    });
});
