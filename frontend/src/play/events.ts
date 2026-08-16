import type { CompanyView, EventView, PositionView, TableViewResponse } from "../api/views";

export interface TableState {
    readonly seq: number;
    readonly view: PositionView;
    readonly company: CompanyView;
}

export function openedFrom(response: TableViewResponse): TableState {
    return { seq: response.seq, view: response.view, company: response.company };
}

export function advanced(state: TableState, event: EventView): TableState {
    if (event.seq < state.seq) {
        return state;
    }
    return { seq: event.seq + 1, view: event.position, company: state.company };
}

export function accompanied(state: TableState, company: CompanyView): TableState {
    return { ...state, company };
}

export function refreshed(state: TableState, response: TableViewResponse): TableState {
    if (response.seq < state.seq) {
        return state;
    }
    return openedFrom(response);
}

export function gathered(company: CompanyView): boolean {
    return company.seats.every((seated) => seated.claimed);
}

export function seatedAs(view: PositionView): number | null {
    for (const [seat, rack] of Object.entries(view.racks)) {
        if (rack !== null) {
            return Number(seat);
        }
    }
    return null;
}
