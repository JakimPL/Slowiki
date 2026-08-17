import { useCallback, useState } from "react";

import { rememberNotices, requestedNotices, storedNotices } from "./notices";

export interface NoticeHold {
    readonly wanted: boolean;
    readonly flip: () => void;
}

export function useNotices(): NoticeHold {
    const [wanted, setWanted] = useState(() => (typeof window === "undefined" ? false : storedNotices(localStorage)));

    const flip = useCallback((): void => {
        if (wanted) {
            rememberNotices(false, localStorage);
            setWanted(false);
            return;
        }
        void requestedNotices().then((granted) => {
            rememberNotices(granted, localStorage);
            setWanted(granted);
        });
    }, [wanted]);

    return { wanted, flip };
}
