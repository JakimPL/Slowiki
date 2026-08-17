import { useEffect, useRef } from "react";

import { buzzed, retitled, TURN_BUZZ } from "./alerts";

export function useAlerts(acting: boolean, baseTitle: string): void {
    const wasActing = useRef(false);

    useEffect(() => {
        document.title = retitled(baseTitle, acting);
        if (acting && !wasActing.current) {
            buzzed(navigator, TURN_BUZZ);
        }
        wasActing.current = acting;
    }, [acting, baseTitle]);

    useEffect(
        () => (): void => {
            document.title = baseTitle;
        },
        [baseTitle],
    );
}
