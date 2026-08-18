import type { PointerEvent as ReactPointerEvent } from "react";

import type { Grasp } from "./dragging";

export interface TileBindings {
    readonly lifted: number | null;
    readonly carried: number | null;
    readonly onTap: (grasp: Grasp) => void;
    readonly onDown: (grasp: Grasp, event: ReactPointerEvent<HTMLButtonElement>) => void;
}
