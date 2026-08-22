import { bodyOf } from "./parsing";

export const UNKNOWN_CODE = "unknown";
export const STALE_POSITION_CODE = "stale_position";
export const NO_PREMOVE_CODE = "no_premove";
export const CONFLICT_STATUS = 409;
export const MISSING_STATUS = 404;
export const GONE_STATUS = 410;

export class Refused extends Error {
    readonly status: number;
    readonly code: string;

    constructor(status: number, detail: string, code: string) {
        super(detail);
        this.name = "Refused";
        this.status = status;
        this.code = code;
    }
}

export async function refusalOf(response: Response): Promise<Refused> {
    const fallback = response.statusText === "" ? "the request was refused" : response.statusText;
    let text = "";
    try {
        text = await response.text();
    } catch {
        return new Refused(response.status, fallback, UNKNOWN_CODE);
    }
    try {
        const body = bodyOf<{ detail?: unknown; code?: unknown }>(text);
        const detail = typeof body.detail === "string" ? body.detail : fallback;
        const code = typeof body.code === "string" ? body.code : UNKNOWN_CODE;
        return new Refused(response.status, detail, code);
    } catch {
        return new Refused(response.status, fallback, UNKNOWN_CODE);
    }
}

export function movedOn(trouble: Refused): boolean {
    return trouble.status === CONFLICT_STATUS;
}

export function gone(trouble: unknown): boolean {
    if (!(trouble instanceof Refused)) {
        return false;
    }
    return trouble.status === MISSING_STATUS || trouble.status === GONE_STATUS;
}

export function reasonOf(trouble: unknown): string {
    if (trouble instanceof Refused) {
        return trouble.message;
    }
    if (trouble instanceof Error && trouble.message !== "") {
        return trouble.message;
    }
    return "the table could not be reached";
}
