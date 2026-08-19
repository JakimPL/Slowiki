import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { LoreReading } from "../../../src/api/lore";
import { specimenFor } from "../../../src/play/lore/specimens";
import { WordParadigm } from "../../../src/table/words/WordParadigm";
import { aForm, aReading, someInflection } from "../../fixtures/lore";

const CHOOSE = (): void => undefined;
const RETREAT = (): void => undefined;

function specimenReadings(word: string): readonly LoreReading[] {
    const lore = specimenFor(word);
    if (lore === null) {
        throw new Error(`no specimen for ${word}`);
    }
    return lore.readings;
}

function readingOf(word: string, lexeme: string): LoreReading {
    const reading = specimenReadings(word).find((one) => one.lexeme === lexeme);
    if (reading === undefined) {
        throw new Error(`no reading ${lexeme}`);
    }
    return reading;
}

function sheetOf(readings: readonly LoreReading[], reading: LoreReading, word: string): string {
    return renderToStaticMarkup(
        <WordParadigm readings={readings} reading={reading} word={word} onChoose={CHOOSE} onRetreat={RETREAT} />,
    );
}

function specimenSheet(word: string, lexeme: string): string {
    return sheetOf(specimenReadings(word), readingOf(word, lexeme), word);
}

describe("WordParadigm", () => {
    it("lays a noun out as a case-by-number table with scoped headers", () => {
        const markup = specimenSheet("PIŁA", "rzeczownik:PIŁA:SF");
        expect(markup).toContain('class="paradigm-grid"');
        expect(markup).toContain('<th scope="col">pojedyncza</th>');
        expect(markup).toContain('<th scope="col">mnoga</th>');
        expect(markup).toContain('<th scope="row">mianownik</th>');
        expect(markup).toContain('<th scope="row">wołacz</th>');
        expect(markup).toContain(">piłami</span>");
    });

    it("heads the sheet with the reading's part, base form and shared terms", () => {
        const markup = specimenSheet("PIŁA", "rzeczownik:PIŁA:SF");
        expect(markup).toContain(">rzeczownik</span>piła");
        expect(markup).toContain('class="paradigm-axes">żeński');
    });

    it("marks the form standing on the board and strikes what the dictionary refuses", () => {
        const saw = specimenSheet("PIŁA", "rzeczownik:PIŁA:SF");
        expect(saw).toContain('data-standing="true">piła</span>');
        expect(saw).toContain('data-playable="false">piło</span>');
        const castle = specimenSheet("ZAMEK", "rzeczownik:ZAMEK:SM3");
        expect(castle.match(/data-standing="true"/g)).toHaveLength(2);
        expect(castle).not.toContain("data-playable");
    });

    it("carries a back control and offers the sibling readings of a homonym", () => {
        const markup = specimenSheet("PIŁA", "czasownik:PIĆ:V");
        expect(markup).toContain('aria-label="Back to the word card"');
        expect(markup).toContain(">Back</button>");
        expect(markup).toContain('class="paradigm-strip"');
        expect(markup).toContain('aria-pressed="false"><span class="word-part">rzeczownik</span>piła');
        expect(markup).toContain('aria-pressed="true"><span class="word-part">czasownik</span>pić');
    });

    it("rests the reading strip while a word has one reading", () => {
        const markup = specimenSheet("DOM", "rzeczownik:DOM:SM3");
        expect(markup).not.toContain("paradigm-strip");
        expect(markup).toContain(">Back</button>");
    });

    it("titles a verb's grids by mood and tense and lists its unbound forms", () => {
        const markup = specimenSheet("PISAĆ", "czasownik:PISAĆ:V");
        expect(markup).toContain("<caption>forma osobowa · oznajmujący · teraźniejszy</caption>");
        expect(markup).toContain("<caption>forma przeszła · oznajmujący · przeszły</caption>");
        expect(markup).toContain('<th scope="row">pierwsza</th>');
        expect(markup).toContain('<th scope="row">męskoosobowy</th>');
        expect(markup).toContain('class="paradigm-lists"');
        expect(markup).toContain("<dt>bezokolicznik</dt>");
        expect(markup).toContain(">pisząc</span>");
    });

    it("titles an adjective's grids by number and degree over gender columns", () => {
        const markup = specimenSheet("DROGĄ", "przymiotnik:DROGI:ADJ");
        expect(markup).toContain("<caption>pojedyncza · równy</caption>");
        expect(markup).toContain("<caption>pojedyncza · wyższy</caption>");
        expect(markup).toContain('<th scope="col">żeński</th>');
        expect(markup).toContain('data-standing="true">drogą</span>');
    });

    it("prints a gap where the paradigm has no form", () => {
        const markup = specimenSheet("PISAĆ", "czasownik:PISAĆ:V");
        expect(markup).toContain('class="paradigm-gap">—</span>');
    });

    it("titles a bare list as forms and names the leftovers", () => {
        const invariant = aReading({
            part: "przyimek",
            base: "PRZEZ",
            forms: [aForm({ text: "PRZEZ" }), aForm({ text: "PRZEZE" })],
        });
        const markup = sheetOf([invariant], invariant, "PRZEZ");
        expect(markup).toContain("<dt>forms</dt>");
        expect(markup).toContain(">przez</span>");
        expect(markup).toContain(">przeze</span>");
        expect(markup).not.toContain("paradigm-grid");
    });

    it("keeps a form its grid has no room for among the other forms", () => {
        const partial = aReading({
            forms: [
                aForm({ text: "PIŁA", tags: someInflection({ cases: ["mianownik"], number: "pojedyncza" }) }),
                aForm({ text: "PIŁOWI", tags: someInflection({ cases: ["celownik"] }) }),
            ],
        });
        const markup = sheetOf([partial], partial, "PIŁA");
        expect(markup).toContain("<dt>other forms</dt>");
        expect(markup).toContain(">piłowi</span>");
    });
});
