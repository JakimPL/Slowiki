import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { loreFor, SAMPLE_SOURCE } from "../../../src/play/lore/lore";
import type { LoreAnswer } from "../../../src/play/lore/readings";
import { NO_LORE_ANSWER } from "../../../src/play/lore/readings";
import type { AskedWord } from "../../../src/play/words/asked";
import type { WordChip } from "../../../src/play/words/chips";
import { WordPanel } from "../../../src/table/words/WordPanel";
import { aForm, aLore, aReading, someInflection } from "../../fixtures/lore";

const CHIP: WordChip = { text: "PIŁA", points: 7, status: "valid" };
const NOTHING = (): void => undefined;
const DEEPEN = (): void => undefined;

function panelOf(chip: AskedWord, answer: LoreAnswer, lexeme: string | null): string {
    return wordsPanelOf([chip], 0, answer, lexeme);
}

function wordsPanelOf(words: readonly AskedWord[], chosen: number, answer: LoreAnswer, lexeme: string | null): string {
    const asked = words[chosen];
    if (asked === undefined) {
        throw new Error("the panel needs a word");
    }
    return renderToStaticMarkup(
        <WordPanel
            asked={asked}
            words={words}
            chosen={chosen}
            answer={answer}
            lexeme={lexeme}
            onChoose={NOTHING}
            onDeepen={DEEPEN}
            onRetreat={NOTHING}
            onClose={NOTHING}
        />,
    );
}

function cardOf(chip: AskedWord, answer: LoreAnswer): string {
    return panelOf(chip, answer, null);
}

function readyWith(lore: LoreAnswer["lore"], sample: boolean): LoreAnswer {
    return { state: "ready", lore, sample };
}

const ACROSS: AskedWord = { text: "PIŁA", points: null, status: "standing" };
const DOWN: AskedWord = { text: "KOT", points: null, status: "standing" };

describe("WordPanel", () => {
    it("stands in the sheet stratum as a dialog for the word it opened for", () => {
        const markup = cardOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).toContain('class="sheet-region"');
        expect(markup).toContain('class="sheet-scrim"');
        expect(markup).toContain('aria-label="Close the word panel"');
        expect(markup).toContain('role="dialog"');
        expect(markup).toContain('data-depth="card"');
        expect(markup).toContain('aria-label="PIŁA — dictionary reading"');
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).toContain(">7</span>");
    });

    it("stacks a homonym's readings, each with its part, base form and odmiana", () => {
        const markup = cardOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).toContain(">rzeczownik</span>piła");
        expect(markup).toContain("mianownik · pojedyncza · żeński");
        expect(markup).toContain(">czasownik</span>pić");
        expect(markup).toContain("forma przeszła");
        expect(markup.match(/class="word-reading"/g)).toHaveLength(2);
    });

    it("badges sample data and rests once the answer is served", () => {
        expect(cardOf(CHIP, readyWith(aLore(), true))).toContain("sample data");
        expect(cardOf(CHIP, readyWith(aLore(), false))).not.toContain("sample data");
    });

    it("carries the dictionary's verdict, and stays silent while it is unknown", () => {
        expect(cardOf(CHIP, readyWith(aLore(), false))).toContain("in the dictionary");
        const unknown = cardOf({ ...CHIP, status: "unknown" }, readyWith(aLore(), false));
        expect(unknown).not.toContain("word-verdict");
    });

    it("reads a refused word as a note, with no reading to show", () => {
        const markup = cardOf({ ...CHIP, status: "invalid" }, readyWith(loreFor("PIŁA", false), SAMPLE_SOURCE));
        expect(markup).toContain("not in the dictionary");
        expect(markup).toContain("there is no reading");
        expect(markup).not.toContain("word-reading");
    });

    it("says plainly that a playable word carries no analysis", () => {
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [] }), false));
        expect(markup).toContain("no analysis");
        expect(markup).toContain("The word plays.");
    });

    it("prints one odmiana line per bundle the asked form stands in", () => {
        const syncretic = aReading({
            forms: [
                aForm({ tags: someInflection({ cases: ["mianownik"], number: "pojedyncza" }) }),
                aForm({ tags: someInflection({ cases: ["wołacz"], number: "pojedyncza" }) }),
                aForm({ text: "PIŁY", tags: someInflection({ cases: ["dopełniacz"], number: "pojedyncza" }) }),
            ],
        });
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [syncretic] }), false));
        expect(markup).toContain("mianownik · pojedyncza");
        expect(markup).toContain("wołacz · pojedyncza");
        expect(markup).not.toContain("dopełniacz");
    });

    it("holds the asking and failed answers as their own notes", () => {
        expect(cardOf(CHIP, NO_LORE_ANSWER)).toContain("Reading the word");
        expect(cardOf(CHIP, { state: "failed", lore: null, sample: false })).toContain("could not be read");
    });

    it("offers the whole odmiana on every reading of the card", () => {
        const markup = cardOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup.match(/class="word-deepen"/g)).toHaveLength(2);
        expect(markup).toContain("Cała odmiana");
    });

    it("grows into the odmiana sheet for the chosen reading", () => {
        const markup = panelOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE), "czasownik:PIĆ:V");
        expect(markup).toContain('data-depth="paradigm"');
        expect(markup).toContain('aria-label="PIŁA — dictionary reading"');
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).toContain("<caption>forma przeszła · oznajmujący · przeszły</caption>");
        expect(markup).not.toContain("word-deepen");
    });

    it("stands at the card while the chosen reading is stale", () => {
        const markup = panelOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE), "czasownik:PISAĆ:V");
        expect(markup).toContain('data-depth="card"');
        expect(markup).not.toContain("paradigm");
    });

    it("stands at the card while the answer carries no reading to deepen", () => {
        expect(panelOf(CHIP, NO_LORE_ANSWER, "rzeczownik:PIŁA:SF")).toContain('data-depth="card"');
        expect(panelOf(CHIP, readyWith(aLore({ readings: [] }), false), "rzeczownik:PIŁA:SF")).toContain(
            'data-depth="card"',
        );
    });

    it("prints the state alone for a word read off the board, where no score is known", () => {
        const markup = cardOf(ACROSS, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).not.toContain("word-score");
        expect(markup).toContain('data-status="standing"');
        expect(markup).toContain(">standing</span>");
    });

    it("offers a strip where two words cross the held square, marking the one it reads", () => {
        const markup = wordsPanelOf([ACROSS, DOWN], 1, readyWith(loreFor("KOT", true), SAMPLE_SOURCE), null);
        expect(markup).toContain('aria-label="Words at this square"');
        expect(markup).toContain('class="word-tab" aria-pressed="false"');
        expect(markup).toContain('class="word-tab" aria-pressed="true"');
        expect(markup).toContain(">KOT</h2>");
        expect(markup.indexOf("word-strip")).toBeLessThan(markup.indexOf("word-head"));
    });

    it("keeps the strip away from a square carrying one word", () => {
        const markup = cardOf(ACROSS, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).not.toContain("word-strip");
    });

    it("leaves the word strip for the card, so the sheet keeps the reading strip", () => {
        const lore = loreFor("PIŁA", true);
        const lexeme = lore.readings[0]?.lexeme ?? null;
        const markup = wordsPanelOf([ACROSS, DOWN], 0, readyWith(lore, SAMPLE_SOURCE), lexeme);
        expect(markup).toContain('data-depth="paradigm"');
        expect(markup).not.toContain("word-strip");
    });
});
