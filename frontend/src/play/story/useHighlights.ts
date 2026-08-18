import { useEffect, useState } from "react";

import { readHighlights } from "../../api/client";
import type { GameHighlights } from "../../api/highlights";
import type { Seat } from "../../api/seat";

export function useHighlights(seat: Seat, over: boolean): GameHighlights | null {
    const [highlights, setHighlights] = useState<GameHighlights | null>(null);

    useEffect(() => {
        if (!over) {
            return;
        }
        let alive = true;
        readHighlights(seat)
            .then((served) => {
                if (alive) {
                    setHighlights(served);
                }
            })
            .catch(() => undefined);
        return (): void => {
            alive = false;
        };
    }, [seat, over]);

    return highlights;
}
