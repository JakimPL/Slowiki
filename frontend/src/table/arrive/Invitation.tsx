import type { ReactElement } from "react";

import { useCopy } from "../../play/device/useCopy";
import { invitationTo } from "../../play/seats/session";
import { INVITE_BUTTON, INVITE_COPIED } from "../strings";
import { CodeChip } from "./CodeChip";

export interface InvitationProps {
    readonly code: string;
}

export function Invitation({ code }: InvitationProps): ReactElement {
    const { copied, copy } = useCopy();
    return (
        <span className="invitation">
            <CodeChip code={code} />
            <button
                type="button"
                className="invitation-copy"
                onClick={(): void => {
                    copy(invitationTo(window.location.origin, window.location.pathname, code));
                }}
            >
                {copied ? INVITE_COPIED : INVITE_BUTTON}
            </button>
        </span>
    );
}
