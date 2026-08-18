import type { WordChip } from "./chips";

export interface WordPanel {
    readonly chip: WordChip | null;
    readonly lexeme: string | null;
}

export const PANEL_CLOSED: WordPanel = { chip: null, lexeme: null };

export function opened(chip: WordChip): WordPanel {
    return { chip, lexeme: null };
}

export function deepened(panel: WordPanel, lexeme: string): WordPanel {
    return panel.chip === null ? panel : { chip: panel.chip, lexeme };
}

export function retreated(panel: WordPanel): WordPanel {
    if (panel.chip !== null && panel.lexeme !== null) {
        return { chip: panel.chip, lexeme: null };
    }
    return PANEL_CLOSED;
}

export function panelStanding(panel: WordPanel): boolean {
    return panel.chip !== null;
}
