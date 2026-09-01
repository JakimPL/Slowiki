import type { ReactElement } from "react";

import type { Mode } from "../../play/device/mode";
import { MODES } from "../../play/device/mode";
import type { Motion } from "../../play/device/motion";
import { MOTIONS } from "../../play/device/motion";
import { useNotices } from "../../play/device/useNotices";
import { useSettings } from "../../play/settings/useSettings";
import { Invitation } from "../arrive/Invitation";
import { useSheetFocus } from "../input/useSheetFocus";
import {
    MENU_CLOSE,
    MENU_HEADING,
    MENU_INVITATION,
    MODE_CAPTIONS,
    MODE_LABEL,
    MOTION_CAPTIONS,
    MOTION_LABEL,
    NOTICE_CAPTIONS,
    NOTICE_LABEL,
    NOTICE_NOTE,
    TABLE_LEAVE,
} from "../strings";
import { Choice } from "./Choice";
import type { Option } from "./Options";

const NOTICE_OPTIONS: readonly Option<boolean>[] = [
    { value: false, caption: NOTICE_CAPTIONS.off },
    { value: true, caption: NOTICE_CAPTIONS.on },
];

const MODE_OPTIONS: readonly Option<Mode>[] = MODES.map((mode) => ({ value: mode, caption: MODE_CAPTIONS[mode] }));

const MOTION_OPTIONS: readonly Option<Motion>[] = MOTIONS.map((motion) => ({
    value: motion,
    caption: MOTION_CAPTIONS[motion],
}));

export interface TableMenuProps {
    readonly code: string | null;
    readonly onLeave: () => void;
    readonly onClose: () => void;
}

export function TableMenu({ code, onLeave, onClose }: TableMenuProps): ReactElement {
    const { settings, change } = useSettings();
    const { wanted, choose } = useNotices();
    const sheet = useSheetFocus<HTMLDivElement>();
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={MENU_CLOSE} onClick={onClose} />
            <div className="sheet menu" role="dialog" aria-label={MENU_HEADING} tabIndex={-1} ref={sheet}>
                <h2 className="sheet-heading">{MENU_HEADING}</h2>
                {code === null ? null : (
                    <div className="menu-row">
                        <span className="menu-label">{MENU_INVITATION}</span>
                        <Invitation code={code} />
                    </div>
                )}
                <Choice
                    label={NOTICE_LABEL}
                    note={NOTICE_NOTE}
                    options={NOTICE_OPTIONS}
                    chosen={wanted}
                    onChoose={choose}
                />
                <Choice
                    label={MODE_LABEL}
                    note={null}
                    options={MODE_OPTIONS}
                    chosen={settings.mode}
                    onChoose={(mode): void => {
                        change({ mode });
                    }}
                />
                <Choice
                    label={MOTION_LABEL}
                    note={null}
                    options={MOTION_OPTIONS}
                    chosen={settings.motion}
                    onChoose={(motion): void => {
                        change({ motion });
                    }}
                />
                <button type="button" className="action action-quiet" onClick={onLeave}>
                    {TABLE_LEAVE}
                </button>
            </div>
        </div>
    );
}
