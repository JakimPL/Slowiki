import type { ReactElement } from "react";

import { nextMotion } from "../../play/device/motion";
import { useSettings } from "../../play/settings/useSettings";
import { MOTION_CAPTIONS, MOTION_LABEL } from "../strings";

export function MotionToggle(): ReactElement {
    const { settings, change } = useSettings();
    const advance = (): void => {
        change({ motion: nextMotion(settings.motion) });
    };
    return (
        <button type="button" className="chip chip-mode" aria-label={MOTION_LABEL} onClick={advance}>
            {MOTION_CAPTIONS[settings.motion]}
        </button>
    );
}
