import { useCallback } from "react";

import { useSettings } from "../settings/useSettings";
import { requestedNotices } from "./notices";

export interface NoticeHold {
    readonly wanted: boolean;
    readonly flip: () => void;
}

export function useNotices(): NoticeHold {
    const { settings, change } = useSettings();
    const wanted = settings.notices;

    const flip = useCallback((): void => {
        if (wanted) {
            change({ notices: false });
            return;
        }
        void requestedNotices().then((granted) => {
            change({ notices: granted });
        });
    }, [wanted, change]);

    return { wanted, flip };
}
