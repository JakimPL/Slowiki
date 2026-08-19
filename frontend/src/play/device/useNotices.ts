import { useCallback } from "react";

import { useSettings } from "../settings/useSettings";
import { requestedNotices } from "./notices";

export interface NoticeHold {
    readonly wanted: boolean;
    readonly choose: (wanted: boolean) => void;
}

export function useNotices(): NoticeHold {
    const { settings, change } = useSettings();

    const choose = useCallback(
        (wanted: boolean): void => {
            if (!wanted) {
                change({ notices: false });
                return;
            }
            void requestedNotices().then((granted) => {
                change({ notices: granted });
            });
        },
        [change],
    );

    return { wanted: settings.notices, choose };
}
