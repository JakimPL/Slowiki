import { useCallback, useEffect, useState } from "react";

import { copiedText } from "./copying";

export interface CopyHold {
    readonly copied: boolean;
    readonly copy: (text: string) => void;
}

const COPIED_LINGER_MS = 1600;

export function useCopy(): CopyHold {
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (!copied) {
            return;
        }
        const timer = window.setTimeout(() => {
            setCopied(false);
        }, COPIED_LINGER_MS);
        return (): void => {
            window.clearTimeout(timer);
        };
    }, [copied]);

    const copy = useCallback((text: string): void => {
        void copiedText(text).then(setCopied);
    }, []);

    return { copied, copy };
}
