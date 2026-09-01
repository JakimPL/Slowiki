export interface OpenLayers {
    readonly confirm: boolean;
    readonly letters: boolean;
    readonly inspected: boolean;
    readonly rules: boolean;
}

export type Layer = "confirm" | "letters" | "inspected" | "rules" | null;

export function innermost(open: OpenLayers): Layer {
    if (open.confirm) {
        return "confirm";
    }
    if (open.letters) {
        return "letters";
    }
    if (open.inspected) {
        return "inspected";
    }
    return open.rules ? "rules" : null;
}
