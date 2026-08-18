import type { ReactElement } from "react";

import { appliedLocale, nextLocale, rememberLocale } from "../../play/device/locale";
import { activeLocale } from "../../text/active";
import { LOCALE_CAPTION, LOCALE_LABEL } from "../strings";

export function LocaleToggle(): ReactElement {
    const advance = (): void => {
        const upcoming = nextLocale(activeLocale());
        rememberLocale(upcoming, window.localStorage);
        appliedLocale(upcoming, document.documentElement);
        window.location.reload();
    };
    return (
        <button type="button" className="chip chip-mode" aria-label={LOCALE_LABEL} onClick={advance}>
            {LOCALE_CAPTION}
        </button>
    );
}
