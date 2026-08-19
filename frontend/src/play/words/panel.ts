import type { AskedWord } from "./asked";

export interface WordPanel {
    readonly words: readonly AskedWord[];
    readonly chosen: number;
    readonly lexeme: string | null;
}

export const PANEL_CLOSED: WordPanel = { words: [], chosen: 0, lexeme: null };

export function opened(words: readonly AskedWord[]): WordPanel {
    if (words.length === 0) {
        return PANEL_CLOSED;
    }
    return { words, chosen: 0, lexeme: null };
}

export function chose(panel: WordPanel, chosen: number): WordPanel {
    if (panel.words[chosen] === undefined) {
        return panel;
    }
    return { words: panel.words, chosen, lexeme: null };
}

export function deepened(panel: WordPanel, lexeme: string): WordPanel {
    return panelStanding(panel) ? { words: panel.words, chosen: panel.chosen, lexeme } : panel;
}

export function retreated(panel: WordPanel): WordPanel {
    if (panelStanding(panel) && panel.lexeme !== null) {
        return { words: panel.words, chosen: panel.chosen, lexeme: null };
    }
    return PANEL_CLOSED;
}

export function panelStanding(panel: WordPanel): boolean {
    return panel.words.length > 0;
}

export function askedWord(panel: WordPanel): AskedWord | null {
    return panel.words[panel.chosen] ?? null;
}
