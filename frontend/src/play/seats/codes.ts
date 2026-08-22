import type { Schemas } from "../../api/views";

export type CodeShape = Schemas["JoinCodeShape"];

const FRAGMENT_MARK = "#";
const CODE_FIELD = "code";

export function keptCode(text: string, shape: CodeShape): string {
    let kept = "";
    for (const letter of text.toUpperCase()) {
        if (kept.length === shape.length) {
            return kept;
        }
        if (shape.alphabet.includes(letter)) {
            kept += letter;
        }
    }
    return kept;
}

export function codeIn(text: string, shape: CodeShape): string | null {
    const written = text.trim();
    const candidate = (codeFieldIn(written) ?? written).toUpperCase();
    return keptCode(candidate, shape) === candidate && candidate.length === shape.length ? candidate : null;
}

export function enteredCode(text: string, shape: CodeShape): string {
    return codeIn(text, shape) ?? keptCode(text, shape);
}

function codeFieldIn(text: string): string | null {
    const cut = text.indexOf(FRAGMENT_MARK);
    if (cut === -1) {
        return null;
    }
    return new URLSearchParams(text.slice(cut + 1)).get(CODE_FIELD);
}
