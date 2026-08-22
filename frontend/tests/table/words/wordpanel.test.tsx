import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { loreFor } from "../../../src/play/lore/lore";
import type { LoreAnswer } from "../../../src/play/lore/readings";
import { NO_LORE_ANSWER } from "../../../src/play/lore/readings";
import type { AskedWord } from "../../../src/play/words/asked";
import type { WordChip } from "../../../src/play/words/chips";
import { WordPanel } from "../../../src/table/words/WordPanel";
import { aForm, aLore, aReading, someInflection } from "../../fixtures/lore";
import { specimenLore } from "../../fixtures/specimens";

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

function readyWith(lore: LoreAnswer["lore"]): LoreAnswer {
    return { state: "ready", lore };
}

const ACROSS: AskedWord = { text: "PIŁA", points: null, status: "standing" };
const DOWN: AskedWord = { text: "KOT", points: null, status: "standing" };

describe("WordPanel", () => {
    it("stands in the sheet stratum as a dialog for the word it opened for", () => {
        const markup = cardOf(CHIP, readyWith(specimenLore("PIŁA")));
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
        const markup = cardOf(CHIP, readyWith(specimenLore("PIŁA")));
        expect(markup).toContain(">rzeczownik</span>piła");
        expect(markup).toContain("mianownik · pojedyncza · żeński");
        expect(markup).toContain(">czasownik</span>pić");
        expect(markup).toContain("forma przeszła");
        expect(markup.match(/class="word-reading"/g)).toHaveLength(2);
    });

    it("carries the dictionary's verdict, and stays silent while it is unknown", () => {
        expect(cardOf(CHIP, readyWith(aLore()))).toContain("in the dictionary");
        const unknown = cardOf({ ...CHIP, status: "unknown" }, readyWith(aLore()));
        expect(unknown).not.toContain("word-verdict");
    });

    it("reads a refused word as a note, with no reading to show", () => {
        const markup = cardOf({ ...CHIP, status: "invalid" }, readyWith(loreFor("PIŁA", false)));
        expect(markup).toContain("not in the dictionary");
        expect(markup).toContain("there is no reading");
        expect(markup).not.toContain("word-reading");
    });

    it("says plainly that a playable word carries no analysis", () => {
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [] })));
        expect(markup).toContain("no analysis");
        expect(markup).toContain("The word plays.");
    });

    it("prints one odmiana line per bundle the asked form stands in", () => {
        const syncretic = aReading({
            forms: [
                aForm({ tags: someInflection({ cases: ["mianownik"], numbers: ["pojedyncza"] }) }),
                aForm({ tags: someInflection({ cases: ["wołacz"], numbers: ["pojedyncza"] }) }),
                aForm({ text: "PIŁY", tags: someInflection({ cases: ["dopełniacz"], numbers: ["pojedyncza"] }) }),
            ],
        });
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [syncretic] })));
        expect(markup).toContain("mianownik · pojedyncza");
        expect(markup).toContain("wołacz · pojedyncza");
        expect(markup).not.toContain("dopełniacz");
    });

    it("holds the asking and failed answers as their own notes", () => {
        expect(cardOf(CHIP, NO_LORE_ANSWER)).toContain("Reading the word");
        expect(cardOf(CHIP, { state: "failed", lore: null })).toContain("could not be read");
    });

    it("offers the whole odmiana on every reading of the card", () => {
        const markup = cardOf(CHIP, readyWith(specimenLore("PIŁA")));
        expect(markup.match(/class="word-deepen"/g)).toHaveLength(2);
        expect(markup).toContain("Cała odmiana");
    });

    it("grows into the odmiana sheet for the chosen reading", () => {
        const markup = panelOf(CHIP, readyWith(specimenLore("PIŁA")), "czasownik:PIĆ:V");
        expect(markup).toContain('data-depth="paradigm"');
        expect(markup).toContain('aria-label="PIŁA — dictionary reading"');
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).toContain("<caption>forma przeszła · oznajmujący · przeszły</caption>");
        expect(markup).not.toContain("word-deepen");
    });

    it("stands at the card while the chosen reading is stale", () => {
        const markup = panelOf(CHIP, readyWith(specimenLore("PIŁA")), "czasownik:PISAĆ:V");
        expect(markup).toContain('data-depth="card"');
        expect(markup).not.toContain("paradigm");
    });

    it("stands at the card while the answer carries no reading to deepen", () => {
        expect(panelOf(CHIP, NO_LORE_ANSWER, "rzeczownik:PIŁA:SF")).toContain('data-depth="card"');
        expect(panelOf(CHIP, readyWith(aLore({ readings: [] })), "rzeczownik:PIŁA:SF")).toContain('data-depth="card"');
    });

    it("prints the state alone for a word read off the board, where no score is known", () => {
        const markup = cardOf(ACROSS, readyWith(specimenLore("PIŁA")));
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).not.toContain("word-score");
        expect(markup).toContain('data-status="standing"');
        expect(markup).toContain(">standing</span>");
    });

    it("offers a strip where two words cross the held square, marking the one it reads", () => {
        const markup = wordsPanelOf([ACROSS, DOWN], 1, readyWith(specimenLore("KOT")), null);
        expect(markup).toContain('aria-label="Words at this square"');
        expect(markup).toContain('class="word-tab" aria-pressed="false"');
        expect(markup).toContain('class="word-tab" aria-pressed="true"');
        expect(markup).toContain(">KOT</h2>");
        expect(markup.indexOf("word-strip")).toBeLessThan(markup.indexOf("word-head"));
    });

    it("keeps the strip away from a square carrying one word", () => {
        const markup = cardOf(ACROSS, readyWith(specimenLore("PIŁA")));
        expect(markup).not.toContain("word-strip");
    });

    it("leaves the word strip for the card, so the sheet keeps the reading strip", () => {
        const lore = specimenLore("PIŁA");
        const lexeme = lore.readings[0]?.lexeme ?? null;
        const markup = wordsPanelOf([ACROSS, DOWN], 0, readyWith(lore), lexeme);
        expect(markup).toContain('data-depth="paradigm"');
        expect(markup).not.toContain("word-strip");
    });
});
