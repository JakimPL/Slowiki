import type { CSSProperties, ReactElement } from "react";
import { useEffect, useRef, useState } from "react";

import { passMove, playMove } from "../api/moves";
import type { Tile } from "../api/views";
import type { Connection } from "../play/connection";
import type { Draft } from "../play/draft";
import { draftedIdentifiers, placementsOf, shownTile } from "../play/draft";
import type { TableState } from "../play/events";
import { seatedAs } from "../play/events";
import { invalidTextsOf, wordStatusFor } from "../play/feedback";
import { guidanceFor } from "../play/guidance";
import { prospectOf } from "../play/prospects";
import { rulesFrom } from "../play/rules";
import { liftedIdentifier } from "../play/selection";
import type { StoryKind } from "../play/story";
import { storyFor } from "../play/story";
import { tintFor } from "../play/tints";
import { useDescription } from "../play/useDescription";
import { useDesk } from "../play/useDesk";
import { usePlay } from "../play/usePlay";
import type { Arrival } from "../play/useStanding";
import { BlankPicker } from "./BlankPicker";
import { Board } from "./Board";
import { Controls } from "./Controls";
import { GameOver } from "./GameOver";
import type { KeyHandlers } from "./keys";
import { boundKeys } from "./keys";
import { Plaques } from "./Plaques";
import { Rack } from "./Rack";
import { Room } from "./Room";
import type { StatusTone } from "./StatusLine";
import { StatusLine } from "./StatusLine";
import { bagCaption, captionFor, CONNECTION_CAPTIONS, guidanceCaption, primaryCaption } from "./strings";
import { Words } from "./Words";

export interface TableProps {
    readonly arrival: Arrival;
    readonly connection: Connection;
    readonly state: TableState;
    readonly trouble: string | null;
}

export function Table({ arrival, connection, state, trouble }: TableProps): ReactElement {
    const mySeat = arrival.seated ?? seatedAs(state.view);
    const description = useDescription(arrival.seat);
    const { desk, perform } = useDesk(state.view, mySeat);
    const { busy, notice, noticeCode, send } = usePlay(arrival.seat, state.seq);
    const [blankCell, setBlankCell] = useState<number | null>(null);

    const story = storyFor(state.view, state.company, mySeat);
    const present = state.company.seats.filter((seated) => seated.claimed).length;
    const gathering = present < state.company.seats.length;
    const rack = mySeat === null ? null : (state.view.racks[String(mySeat)] ?? null);
    const style: CSSProperties = mySeat === null ? {} : { "--tint": tintFor(mySeat).hex };

    const rules = rulesFrom(description);
    const acting = mySeat !== null && state.view.to_act.includes(mySeat);
    const asPremove = !acting && rules.premovesAllowed;
    const atDesk = mySeat !== null && rack !== null && !gathering && state.view.phase === "turn";
    const mayAct = atDesk && (acting || rules.premovesAllowed);

    const prospect = prospectOf(state.view.board, desk.draft, rules);
    const armed = mayAct && prospect.verdict === "playable";
    const heldBack = draftedIdentifiers(desk.draft);
    const shownRack = rack === null ? null : rack.filter((tile) => !heldBack.has(tile.identifier));
    const guidance = notice ?? guidanceCaption(guidanceFor(prospect.verdict, desk.lift !== null));
    const invalidTexts = invalidTextsOf(noticeCode, notice);
    const chips = prospect.words.map((word) => ({
        ...word,
        status: wordStatusFor(rules.feedback, word.text, invalidTexts),
    }));

    const lay = (cell: number): void => {
        if (!mayAct || desk.lift === null) {
            return;
        }
        if (desk.lift.tile.blank) {
            setBlankCell(cell);
            return;
        }
        perform({ kind: "lay", cell, letter: null });
    };
    const pick = (symbol: string): void => {
        if (blankCell !== null) {
            perform({ kind: "lay", cell: blankCell, letter: symbol });
        }
        setBlankCell(null);
    };
    const play = (): void => {
        if (armed && !busy) {
            send(playMove(mySeat, placementsOf(desk.draft, state.view.board.size)), asPremove);
        }
    };
    const pass = (): void => {
        if (mayAct && !busy) {
            send(passMove(mySeat), asPremove);
        }
    };
    const retreat = (): void => {
        if (blankCell !== null) {
            setBlankCell(null);
            return;
        }
        perform({ kind: desk.lift !== null ? "clear-lift" : "recall" });
    };

    const keysRef = useRef<KeyHandlers>({ onEscape: () => undefined, onEnter: () => undefined });
    useEffect(() => {
        keysRef.current = { onEscape: retreat, onEnter: play };
    });
    useEffect(
        () =>
            boundKeys(document, {
                onEscape: (): void => {
                    keysRef.current.onEscape();
                },
                onEnter: (): void => {
                    keysRef.current.onEnter();
                },
            }),
        [],
    );

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
                <Board
                    board={state.view.board}
                    pending={pendingFacesOf(desk.draft)}
                    targeting={mayAct && desk.lift !== null}
                    onLay={mayAct ? lay : null}
                    onTakeBack={
                        atDesk
                            ? (cell): void => {
                                  perform({ kind: "take-back", cell });
                              }
                            : null
                    }
                />
            </div>
            {gathering ? (
                <Room
                    table={arrival.seat.table}
                    code={arrival.code}
                    present={present}
                    total={state.company.seats.length}
                />
            ) : null}
            {atDesk && chips.length > 0 ? <Words chips={chips} bingo={prospect.bingo ? rules.bingoBonus : 0} /> : null}
            {atDesk && guidance !== null ? (
                <p className="guidance" role="status" data-tone={notice !== null ? "danger" : "hint"}>
                    {guidance}
                </p>
            ) : null}
            {shownRack !== null && shownRack.length > 0 ? (
                <Rack
                    tiles={shownRack}
                    liftedId={liftedIdentifier(desk.lift)}
                    onLift={
                        atDesk
                            ? (tile: Tile): void => {
                                  perform({ kind: "lift", tile });
                              }
                            : null
                    }
                />
            ) : null}
            {atDesk ? (
                <Controls
                    caption={primaryCaption(asPremove, armed ? prospect.points : null)}
                    armed={armed}
                    premove={asPremove}
                    busy={busy}
                    canRecall={desk.draft.length > 0 || desk.lift !== null}
                    canPass={mayAct && rules.passAllowed}
                    onPlay={play}
                    onRecall={(): void => {
                        perform({ kind: "recall" });
                    }}
                    onPass={pass}
                />
            ) : null}
            {trouble !== null && connection !== "live" ? <p className="trouble">{trouble}</p> : null}
            {blankCell !== null ? (
                <BlankPicker
                    alphabet={rules.alphabet}
                    onPick={pick}
                    onClose={(): void => {
                        setBlankCell(null);
                    }}
                />
            ) : null}
            {story.kind === "over" ? <GameOver view={state.view} company={state.company} story={story} /> : null}
        </div>
    );
}

function pendingFacesOf(draft: Draft): ReadonlyMap<number, Tile> {
    return new Map(draft.map((pending) => [pending.cell, shownTile(pending)]));
}

function toneOf(kind: StoryKind): StatusTone {
    if (kind === "acting") {
        return "acting";
    }
    return kind === "over" ? "over" : "quiet";
}
