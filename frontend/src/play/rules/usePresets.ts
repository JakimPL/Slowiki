import { useEffect, useState } from "react";

import { readPresets } from "../../api/client";
import type { PresetsResponse } from "../../api/tables";

export function usePresets(): PresetsResponse | null {
    const [presets, setPresets] = useState<PresetsResponse | null>(null);
    useEffect(() => {
        let alive = true;
        readPresets()
            .then((served) => {
                if (alive) {
                    setPresets(served);
                }
            })
            .catch(() => undefined);
        return (): void => {
            alive = false;
        };
    }, []);
    return presets;
}
