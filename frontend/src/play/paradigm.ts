import type { InflectedForm, Inflection, LoreReading, Part, VerbForm } from "../api/lore";
import type { Dimension } from "./tagset";
import { compareInflections, DIMENSION_ORDER, orderedTerms, termsOn } from "./tagset";

export interface ParadigmAxis {
    readonly dimension: Dimension;
    readonly terms: readonly string[];
}

export interface ParadigmCell {
    readonly forms: readonly InflectedForm[];
}

export interface ParadigmRow {
    readonly term: string;
    readonly cells: readonly ParadigmCell[];
}

export interface ParadigmGrid {
    readonly titles: readonly string[];
    readonly rowDimension: Dimension;
    readonly columns: ParadigmAxis | null;
    readonly rows: readonly ParadigmRow[];
}

export interface ParadigmList {
    readonly titles: readonly string[];
    readonly forms: readonly InflectedForm[];
}

export interface Paradigm {
    readonly heading: readonly string[];
    readonly grids: readonly ParadigmGrid[];
    readonly lists: readonly ParadigmList[];
    readonly rest: readonly InflectedForm[];
}

interface GridShape {
    readonly rows: Dimension;
    readonly columns: Dimension | null;
}

interface FormGroup {
    readonly shape: GridShape | null;
    readonly titles: readonly string[];
    readonly forms: InflectedForm[];
}

const CASE_BY_NUMBER: GridShape = { rows: "case", columns: "number" };

const CASE_BY_GENDER: GridShape = { rows: "case", columns: "gender" };

const PERSON_BY_NUMBER: GridShape = { rows: "person", columns: "number" };

const GENDER_BY_NUMBER: GridShape = { rows: "gender", columns: "number" };

const BY_DEGREE: GridShape = { rows: "degree", columns: null };

const VERB_SHAPES: Record<VerbForm, GridShape | null> = {
    bezokolicznik: null,
    "forma osobowa": PERSON_BY_NUMBER,
    "forma przeszła": GENDER_BY_NUMBER,
    rozkaźnik: PERSON_BY_NUMBER,
    bezosobnik: null,
    "imiesłów czynny": CASE_BY_GENDER,
    "imiesłów bierny": CASE_BY_GENDER,
    "imiesłów współczesny": null,
    "imiesłów uprzedni": null,
    odsłownik: CASE_BY_NUMBER,
    "końcówka ruchoma": PERSON_BY_NUMBER,
    predykatyw: null,
    winien: GENDER_BY_NUMBER,
};

const GROUP_SEPARATOR = "\u001f";

export function paradigmOf(reading: LoreReading): Paradigm {
    const forms = inCanonicalOrder(reading.forms);
    const headingDimensions = headingDimensionsOf(reading.part, forms);
    const groups = groupedByLayout(reading.part, forms, headingDimensions);
    return {
        heading: headingTermsOf(forms, headingDimensions),
        grids: groups.flatMap(gridOf),
        lists: groups.flatMap(listOf),
        rest: distinctByText(groups.flatMap(unplacedIn)),
    };
}

function inCanonicalOrder(forms: readonly InflectedForm[]): readonly InflectedForm[] {
    return [...forms].sort(byTagsThenText);
}

function byTagsThenText(one: InflectedForm, other: InflectedForm): number {
    const byTags = compareInflections(one.tags, other.tags);
    if (byTags !== 0) {
        return byTags;
    }
    if (one.text === other.text) {
        return 0;
    }
    return one.text < other.text ? -1 : 1;
}

function headingDimensionsOf(part: Part, forms: readonly InflectedForm[]): ReadonlySet<Dimension> {
    const axes = axesOf(part, forms);
    return new Set(DIMENSION_ORDER.filter((dimension) => !axes.has(dimension) && sharedBy(forms, dimension)));
}

function axesOf(part: Part, forms: readonly InflectedForm[]): ReadonlySet<Dimension> {
    const axes = new Set<Dimension>();
    for (const form of forms) {
        const shape = shapeFor(part, form.tags);
        if (shape !== null) {
            axes.add(shape.rows);
            if (shape.columns !== null) {
                axes.add(shape.columns);
            }
        }
    }
    return axes;
}

function sharedBy(forms: readonly InflectedForm[], dimension: Dimension): boolean {
    const leading = forms[0];
    if (leading === undefined) {
        return false;
    }
    const shared = keyOfTerms(termsOn(leading.tags, dimension));
    return forms.every((form) => keyOfTerms(termsOn(form.tags, dimension)) === shared);
}

function headingTermsOf(forms: readonly InflectedForm[], headingDimensions: ReadonlySet<Dimension>): readonly string[] {
    const leading = forms[0];
    if (leading === undefined) {
        return [];
    }
    return DIMENSION_ORDER.filter((dimension) => headingDimensions.has(dimension)).flatMap((dimension) =>
        termsOn(leading.tags, dimension),
    );
}

function groupedByLayout(
    part: Part,
    forms: readonly InflectedForm[],
    headingDimensions: ReadonlySet<Dimension>,
): readonly FormGroup[] {
    const groups = new Map<string, FormGroup>();
    for (const form of forms) {
        const shape = shapeFor(part, form.tags);
        const titles = titlesOf(form.tags, shape, headingDimensions);
        const key = keyOfGroup(shape, titles);
        const standing = groups.get(key);
        if (standing === undefined) {
            groups.set(key, { shape, titles, forms: [form] });
        } else {
            standing.forms.push(form);
        }
    }
    return [...groups.values()];
}

function titlesOf(
    tags: Inflection,
    shape: GridShape | null,
    headingDimensions: ReadonlySet<Dimension>,
): readonly string[] {
    return DIMENSION_ORDER.filter(
        (dimension) => !headingDimensions.has(dimension) && !onAxisOf(shape, dimension),
    ).flatMap((dimension) => termsOn(tags, dimension));
}

function onAxisOf(shape: GridShape | null, dimension: Dimension): boolean {
    if (shape === null) {
        return false;
    }
    return dimension === shape.rows || dimension === shape.columns;
}

function keyOfGroup(shape: GridShape | null, titles: readonly string[]): string {
    const axes = shape === null ? [] : [shape.rows, shape.columns ?? ""];
    return keyOfTerms([...axes, ...titles]);
}

function keyOfTerms(terms: readonly string[]): string {
    return terms.join(GROUP_SEPARATOR);
}

function gridOf(group: FormGroup): readonly ParadigmGrid[] {
    const shape = group.shape;
    if (shape === null) {
        return [];
    }
    const placed = group.forms.filter((form) => placeableIn(form, shape));
    if (placed.length === 0) {
        return [];
    }
    return [griddedBy(placed, group.titles, shape.rows, shape.columns)];
}

function listOf(group: FormGroup): readonly ParadigmList[] {
    if (group.shape !== null) {
        return [];
    }
    return [{ titles: group.titles, forms: distinctByText(group.forms) }];
}

function unplacedIn(group: FormGroup): readonly InflectedForm[] {
    const shape = group.shape;
    if (shape === null) {
        return [];
    }
    return group.forms.filter((form) => !placeableIn(form, shape));
}

function placeableIn(form: InflectedForm, shape: GridShape): boolean {
    if (termsOn(form.tags, shape.rows).length === 0) {
        return false;
    }
    return shape.columns === null || termsOn(form.tags, shape.columns).length > 0;
}

function griddedBy(
    forms: readonly InflectedForm[],
    titles: readonly string[],
    rowDimension: Dimension,
    columnDimension: Dimension | null,
): ParadigmGrid {
    const columnTerms = columnDimension === null ? [] : presentTerms(forms, columnDimension);
    const columnKeys: readonly (string | null)[] = columnDimension === null ? [null] : columnTerms;
    const rows = presentTerms(forms, rowDimension).map((rowTerm) => ({
        term: rowTerm,
        cells: columnKeys.map((columnKey) => ({
            forms: distinctByText(
                forms.filter(
                    (form) => standsIn(form, rowDimension, rowTerm) && standsIn(form, columnDimension, columnKey),
                ),
            ),
        })),
    }));
    return {
        titles,
        rowDimension,
        columns: columnDimension === null ? null : { dimension: columnDimension, terms: columnTerms },
        rows,
    };
}

function standsIn(form: InflectedForm, dimension: Dimension | null, term: string | null): boolean {
    if (dimension === null || term === null) {
        return true;
    }
    return termsOn(form.tags, dimension).includes(term);
}

function presentTerms(forms: readonly InflectedForm[], dimension: Dimension): readonly string[] {
    const present = new Set(forms.flatMap((form) => termsOn(form.tags, dimension)));
    return orderedTerms([...present], dimension);
}

function distinctByText(forms: readonly InflectedForm[]): readonly InflectedForm[] {
    const seen = new Set<string>();
    return forms.filter((form) => {
        if (seen.has(form.text)) {
            return false;
        }
        seen.add(form.text);
        return true;
    });
}

function shapeFor(part: Part, tags: Inflection): GridShape | null {
    switch (part) {
        case "rzeczownik":
        case "liczebnik":
        case "zaimek":
            return CASE_BY_NUMBER;
        case "przymiotnik":
            return CASE_BY_GENDER;
        case "przysłówek":
            return BY_DEGREE;
        case "czasownik":
            return tags.verb_form === null ? null : VERB_SHAPES[tags.verb_form];
        case "przyimek":
        case "spójnik":
        case "partykuła":
        case "wykrzyknik":
        case "inny":
            return null;
    }
}
