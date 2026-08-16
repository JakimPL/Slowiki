import type { CSSProperties, ReactElement } from "react";

import type { Connection } from "../play/connection";
import type { TableState } from "../play/events";
import { seatedAs } from "../play/events";
import type { StoryKind } from "../play/story";
import { storyFor } from "../play/story";
import { tintFor } from "../play/tints";
import type { Arrival } from "../play/useStanding";
import { Board } from "./Board";
import { GameOver } from "./GameOver";
import { Plaques } from "./Plaques";
import { Rack } from "./Rack";
import { Room } from "./Room";
import type { StatusTone } from "./StatusLine";
import { StatusLine } from "./StatusLine";
import { bagCaption, captionFor, CONNECTION_CAPTIONS } from "./strings";

export interface TableProps {
    readonly arrival: Arrival;
    readonly connection: Connection;
    readonly state: TableState;
    readonly trouble: string | null;
}

export function Table({ arrival, connection, state, trouble }: TableProps): ReactElement {
    const mySeat = arrival.seated ?? seatedAs(state.view);
    const story = storyFor(state.view, state.company, mySeat);
    const present = state.company.seats.filter((seated) => seated.claimed).length;
    const gathering = present < state.company.seats.length;
    const rack = mySeat === null ? null : (state.view.racks[String(mySeat)] ?? null);
    const style: CSSProperties = mySeat === null ? {} : { "--tint": tintFor(mySeat).hex };
    return (
        <div className="table" data-acting={story.kind === "acting" ? "true" : undefined} style={style}>
            <header className="status-strip">
                <StatusLine text={captionFor(story, state.company)} tone={toneOf(story.kind)} />
                <span className="chip">{bagCaption(state.view.bag_count)}</span>
                {connection === "live" ? null : (
                    <span className="chip chip-connection" data-connection={connection}>
                        {CONNECTION_CAPTIONS[connection]}
                    </span>
                )}
            </header>
            <Plaques view={state.view} company={state.company} mySeat={mySeat} />
            <div className="board-region">
                <Board board={state.view.board} />
            </div>
            {gathering ? (
                <Room
                    table={arrival.seat.table}
                    code={arrival.code}
                    present={present}
                    total={state.company.seats.length}
                />
            ) : null}
            {rack !== null && rack.length > 0 ? <Rack tiles={rack} /> : null}
            {trouble !== null && connection !== "live" ? <p className="trouble">{trouble}</p> : null}
            {story.kind === "over" ? <GameOver view={state.view} company={state.company} story={story} /> : null}
        </div>
    );
}

function toneOf(kind: StoryKind): StatusTone {
    if (kind === "acting") {
        return "acting";
    }
    return kind === "over" ? "over" : "quiet";
}
