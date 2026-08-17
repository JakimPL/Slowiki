import { useEffect, useState } from "react";

import { readDescription } from "../api/client";
import type { Seat } from "../api/seat";
import type { TableDescription } from "../api/tables";

export function useDescription(seat: Seat): TableDescription | null {
    const [description, setDescription] = useState<TableDescription | null>(null);

    useEffect(() => {
        let alive = true;
        readDescription(seat)
            .then((served) => {
                if (alive) {
                    setDescription(served);
                }
            })
            .catch(() => undefined);
        return (): void => {
            alive = false;
        };
    }, [seat]);

    return description;
}
