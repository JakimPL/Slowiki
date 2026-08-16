export interface Seat {
    readonly table: string;
    readonly token: string | null;
}

export const SEAT_TOKEN_HEADER = "X-Seat-Token";

export function headersFor(seat: Seat): Record<string, string> {
    if (seat.token === null) {
        return {};
    }
    return { [SEAT_TOKEN_HEADER]: seat.token };
}
