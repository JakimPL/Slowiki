import type { ReactElement } from "react";

import { invitationTo } from "../play/session";
import { useCopy } from "../play/useCopy";
import { CodeChip } from "./CodeChip";
import { INVITE_BUTTON, INVITE_COPIED } from "./strings";

export interface InvitationProps {
    readonly table: string;
    readonly code: string;
}

export function Invitation({ table, code }: InvitationProps): ReactElement {
    const { copied, copy } = useCopy();
    return (
        <span className="invitation">
            <CodeChip code={code} />
            <button
                type="button"
                className="invitation-copy"
                onClick={(): void => {
                    copy(invitationTo(window.location.origin, window.location.pathname, table, code));
                }}
            >
                {copied ? INVITE_COPIED : INVITE_BUTTON}
            </button>
        </span>
    );
}
