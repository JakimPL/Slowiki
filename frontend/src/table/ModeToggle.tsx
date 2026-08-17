import type { ReactElement } from "react";
import { useState } from "react";

import type { Mode } from "../play/mode";
import { appliedMode, nextMode, rememberMode, storedMode } from "../play/mode";
import { MODE_CAPTIONS, MODE_LABEL } from "./strings";

export function ModeToggle(): ReactElement {
    const [mode, setMode] = useState<Mode>(() =>
        typeof window === "undefined" ? "system" : storedMode(window.localStorage),
    );
    const advance = (): void => {
        const upcoming = nextMode(mode);
        appliedMode(upcoming, document.documentElement);
        rememberMode(upcoming, window.localStorage);
        setMode(upcoming);
    };
    return (
        <button type="button" className="chip chip-mode" aria-label={MODE_LABEL} onClick={advance}>
            {MODE_CAPTIONS[mode]}
        </button>
    );
}
