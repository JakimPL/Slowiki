import { useState } from "react";

import type { AskedWord } from "./asked";
import type { WordPanel } from "./panel";
import { chose, deepened, opened, PANEL_CLOSED, retreated } from "./panel";

export interface PanelHandle {
    readonly panel: WordPanel;
    readonly open: (words: readonly AskedWord[]) => void;
    readonly choose: (chosen: number) => void;
    readonly deepen: (lexeme: string) => void;
    readonly retreat: () => void;
    readonly close: () => void;
}

export function useWordPanel(): PanelHandle {
    const [panel, setPanel] = useState<WordPanel>(PANEL_CLOSED);
    return {
        panel,
        open: (words: readonly AskedWord[]): void => {
            setPanel(opened(words));
        },
        choose: (chosen: number): void => {
            setPanel((standing) => chose(standing, chosen));
        },
        deepen: (lexeme: string): void => {
            setPanel((standing) => deepened(standing, lexeme));
        },
        retreat: (): void => {
            setPanel(retreated);
        },
        close: (): void => {
            setPanel(PANEL_CLOSED);
        },
    };
}
