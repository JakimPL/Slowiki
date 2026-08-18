import { useState } from "react";

import type { WordChip } from "./chips";
import type { WordPanel } from "./panel";
import { deepened, opened, PANEL_CLOSED, retreated } from "./panel";

export interface PanelHandle {
    readonly panel: WordPanel;
    readonly open: (chip: WordChip) => void;
    readonly deepen: (lexeme: string) => void;
    readonly retreat: () => void;
    readonly close: () => void;
}

export function useWordPanel(): PanelHandle {
    const [panel, setPanel] = useState<WordPanel>(PANEL_CLOSED);
    return {
        panel,
        open: (chip: WordChip): void => {
            setPanel(opened(chip));
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
