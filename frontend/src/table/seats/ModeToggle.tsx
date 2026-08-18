import type { ReactElement } from "react";

import { nextMode } from "../../play/device/mode";
import { useSettings } from "../../play/settings/useSettings";
import { MODE_CAPTIONS, MODE_LABEL } from "../strings";

export function ModeToggle(): ReactElement {
    const { settings, change } = useSettings();
    const advance = (): void => {
        change({ mode: nextMode(settings.mode) });
    };
    return (
        <button type="button" className="chip chip-mode" aria-label={MODE_LABEL} onClick={advance}>
            {MODE_CAPTIONS[settings.mode]}
        </button>
    );
}
