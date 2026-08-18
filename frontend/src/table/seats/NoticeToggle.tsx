import type { ReactElement } from "react";

import { useNotices } from "../../play/device/useNotices";
import { NOTICE_CAPTIONS, NOTICE_LABEL } from "../strings";

export function NoticeToggle(): ReactElement {
    const { wanted, flip } = useNotices();
    return (
        <button type="button" className="chip chip-mode" aria-label={NOTICE_LABEL} aria-pressed={wanted} onClick={flip}>
            {wanted ? NOTICE_CAPTIONS.on : NOTICE_CAPTIONS.off}
        </button>
    );
}
