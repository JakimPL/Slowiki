import { Refused } from "../api/refusal";

export async function delivered(send: () => Promise<number>): Promise<number> {
    try {
        return await send();
    } catch (trouble: unknown) {
        if (trouble instanceof Refused) {
            throw trouble;
        }
        return send();
    }
}
