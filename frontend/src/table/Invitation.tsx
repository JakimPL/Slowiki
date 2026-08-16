import type { ReactElement } from "react";
import { useState } from "react";

import { invitationTo } from "../play/session";
import { INVITE_BUTTON, INVITE_COPIED } from "./strings";

export interface InvitationProps {
    readonly table: string;
    readonly code: string;
}

export function Invitation({ table, code }: InvitationProps): ReactElement {
    const [copied, setCopied] = useState(false);
    const copy = (): void => {
        const link = invitationTo(window.location.origin, window.location.pathname, table, code);
        void navigator.clipboard.writeText(link).then(() => {
            setCopied(true);
        });
    };
    return (
        <span className="invitation">
            <code className="invitation-code">{code}</code>
            <button type="button" className="invitation-copy" onClick={copy}>
                {copied ? INVITE_COPIED : INVITE_BUTTON}
            </button>
        </span>
    );
}
