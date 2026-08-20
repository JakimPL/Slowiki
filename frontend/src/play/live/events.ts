import type { CompanyView, EventView, PositionView, TableViewResponse } from "../../api/views";
import type { LogEntry } from "../story/log";
import { appendedLog, logEntryOf } from "../story/log";

export interface TableState {
    readonly seq: number;
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly log: readonly LogEntry[];
}

export function openedFrom(response: TableViewResponse): TableState {
    return { seq: response.seq, view: response.view, company: response.company, log: [] };
}

export function advanced(state: TableState, event: EventView): TableState {
    if (event.seq < state.seq) {
        return state;
    }
    return {
        seq: event.seq + 1,
        view: event.position,
        company: state.company,
        log: appendedLog(state.log, logEntryOf(event, state.view)),
    };
}

export function accompanied(state: TableState, company: CompanyView): TableState {
    return { ...state, company };
}

export function positioned(state: TableState, view: PositionView): TableState {
    return { ...state, view };
}

export function refreshed(state: TableState, response: TableViewResponse): TableState {
    if (response.seq < state.seq) {
        return state;
    }
    return { ...openedFrom(response), log: state.log };
}

export function seatedAs(view: PositionView): number | null {
    for (const [seat, rack] of Object.entries(view.racks)) {
        if (rack !== null) {
            return Number(seat);
        }
    }
    return null;
}
