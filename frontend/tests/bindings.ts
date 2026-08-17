import type { TileBindings } from "../src/table/bindings";

export function stubBindings(): TileBindings {
    return {
        onTap: () => undefined,
        onDown: () => undefined,
        onMove: () => undefined,
        onUp: () => undefined,
        onCancel: () => undefined,
    };
}
