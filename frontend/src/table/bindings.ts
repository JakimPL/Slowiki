import type { PointerEvent as ReactPointerEvent } from "react";

import type { Grasp } from "./dragging";

export interface TileBindings {
    readonly onTap: (grasp: Grasp) => void;
    readonly onDown: (grasp: Grasp, event: ReactPointerEvent<HTMLButtonElement>) => void;
    readonly onMove: (event: ReactPointerEvent<HTMLButtonElement>) => void;
    readonly onUp: (event: ReactPointerEvent<HTMLButtonElement>) => void;
    readonly onCancel: () => void;
}
