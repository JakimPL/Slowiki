import type { ReactElement } from "react";
import { useState } from "react";

import type { SettingName } from "../../api/tables";
import { RULES_HELP, SETTING_HELP } from "../strings";

const HELP_GLYPH = "?";

export interface HelpProps {
    readonly setting: SettingName;
}

export function Help({ setting }: HelpProps): ReactElement {
    const [open, setOpen] = useState(false);
    const noteId = `help-${setting}`;
    return (
        <>
            <button
                type="button"
                className="rules-help"
                aria-label={RULES_HELP}
                aria-expanded={open}
                aria-controls={noteId}
                onClick={(): void => {
                    setOpen(!open);
                }}
            >
                {HELP_GLYPH}
            </button>
            <span className="rules-help-note" id={noteId} hidden={!open}>
                {SETTING_HELP[setting]}
            </span>
        </>
    );
}
