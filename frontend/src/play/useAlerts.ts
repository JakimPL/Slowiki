import { useEffect, useRef } from "react";

import { buzzed, retitled, TURN_BUZZ } from "./alerts";
import { announced, grantedNotices, noticeDue } from "./notices";

export function useAlerts(acting: boolean, baseTitle: string, notices: boolean, turnCaption: string): void {
    const wasActing = useRef(false);

    useEffect(() => {
        document.title = retitled(baseTitle, acting);
        if (acting && !wasActing.current) {
            buzzed(navigator, TURN_BUZZ);
            if (noticeDue(notices, acting, document.hidden, grantedNotices())) {
                announced(baseTitle, turnCaption);
            }
        }
        wasActing.current = acting;
    }, [acting, baseTitle, notices, turnCaption]);

    useEffect(
        () => (): void => {
            document.title = baseTitle;
        },
        [baseTitle],
    );
}
