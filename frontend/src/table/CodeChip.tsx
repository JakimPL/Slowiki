import type { ReactElement } from "react";

import { useCopy } from "../play/useCopy";
import { COPIED_MARK, COPY_CODE_LABEL } from "./strings";

export interface CodeChipProps {
    readonly code: string;
}

export function CodeChip({ code }: CodeChipProps): ReactElement {
    const { copied, copy } = useCopy();
    return (
        <button
            type="button"
            className="code-chip"
            data-copied={copied ? "true" : undefined}
            aria-label={COPY_CODE_LABEL}
            onClick={(): void => {
                copy(code);
            }}
        >
            {code}
            {copied ? (
                <i className="code-chip-mark" aria-hidden="true">
                    {COPIED_MARK}
                </i>
            ) : null}
        </button>
    );
}
