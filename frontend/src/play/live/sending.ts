import { Refused, STALE_POSITION_CODE } from "../../api/refusal";

const STALE_RETRIES = 3;

export async function delivered(
    send: (base: number) => Promise<number>,
    base: number,
    renewed: () => Promise<number | null>,
): Promise<number> {
    return attempted(send, base, renewed, STALE_RETRIES);
}

async function attempted(
    send: (base: number) => Promise<number>,
    base: number,
    renewed: () => Promise<number | null>,
    left: number,
): Promise<number> {
    try {
        return await send(base);
    } catch (trouble: unknown) {
        if (!(trouble instanceof Refused)) {
            return send(base);
        }
        if (trouble.code !== STALE_POSITION_CODE || left === 0) {
            throw trouble;
        }
        return resubmitted(send, renewed, trouble, left);
    }
}

async function resubmitted(
    send: (base: number) => Promise<number>,
    renewed: () => Promise<number | null>,
    original: Refused,
    left: number,
): Promise<number> {
    const fresh = await renewed();
    if (fresh === null) {
        throw original;
    }
    return attempted(send, fresh, renewed, left - 1);
}
