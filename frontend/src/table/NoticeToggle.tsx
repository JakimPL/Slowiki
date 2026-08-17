import type { ReactElement } from "react";

import { NOTICE_CAPTIONS, NOTICE_LABEL } from "./strings";

export interface NoticeToggleProps {
    readonly wanted: boolean;
    readonly onFlip: () => void;
}

export function NoticeToggle({ wanted, onFlip }: NoticeToggleProps): ReactElement {
    return (
        <button
            type="button"
            className="chip chip-mode"
            aria-label={NOTICE_LABEL}
            aria-pressed={wanted}
            onClick={onFlip}
        >
            {wanted ? NOTICE_CAPTIONS.on : NOTICE_CAPTIONS.off}
        </button>
    );
}
