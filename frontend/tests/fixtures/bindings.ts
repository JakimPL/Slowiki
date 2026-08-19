import type { TileBindings } from "../../src/table/input/bindings";

export function stubBindings(lifted: number | null = null, carried: number | null = null): TileBindings {
    return {
        lifted,
        carried,
        onTap: () => undefined,
        onDown: () => undefined,
    };
}
