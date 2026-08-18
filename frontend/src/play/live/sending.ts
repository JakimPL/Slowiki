import { Refused, STALE_POSITION_CODE } from "../../api/refusal";

export async function delivered(
    send: (base: number) => Promise<number>,
    base: number,
    renewed: () => Promise<number | null>,
): Promise<number> {
    try {
        return await send(base);
    } catch (trouble: unknown) {
        if (!(trouble instanceof Refused)) {
            return send(base);
        }
        if (trouble.code !== STALE_POSITION_CODE) {
            throw trouble;
        }
        return resubmitted(send, renewed, trouble);
    }
}

async function resubmitted(
    send: (base: number) => Promise<number>,
    renewed: () => Promise<number | null>,
    original: Refused,
): Promise<number> {
    const fresh = await renewed();
    if (fresh === null) {
        throw original;
    }
    return send(fresh);
}
