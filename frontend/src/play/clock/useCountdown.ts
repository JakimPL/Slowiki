import { useEffect, useState } from "react";

import type { ClockView } from "../../api/views";
import { remainingSeconds, skewOf } from "./clock";

const TICK_MS = 500;
const MS_PER_SECOND = 1000;

export function useCountdown(clock: ClockView | null): number | null {
    const [remaining, setRemaining] = useState<number | null>(null);

    useEffect(() => {
        if (clock === null) {
            setRemaining(null);
            return;
        }
        const skew = skewOf(clock, Date.now() / MS_PER_SECOND);
        const update = (): void => {
            setRemaining(remainingSeconds(clock, skew, Date.now() / MS_PER_SECOND));
        };
        update();
        const timer = window.setInterval(update, TICK_MS);
        return (): void => {
            window.clearInterval(timer);
        };
    }, [clock]);

    return remaining;
}
