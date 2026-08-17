import type { CSSProperties, ReactElement } from "react";
import { useEffect, useRef, useState } from "react";

import { exchangeMove, passMove, playMove } from "../api/moves";
import { STALE_POSITION_CODE } from "../api/refusal";
import type { ClockView, Tile } from "../api/views";
import { arrangedTiles, shuffledArrangement } from "../play/arrangement";
import { urgencyOf } from "../play/clock";
import type { Connection } from "../play/connection";
import type { DeskEffect } from "../play/desk";
import type { Draft } from "../play/draft";
import { draftedIdentifiers, placementsOf, shownTile } from "../play/draft";
import type { TableState } from "../play/events";
import { seatedAs } from "../play/events";
import { exchangeProspectOf } from "../play/exchange";
import { invalidTextsOf, wordStatusFor } from "../play/feedback";
import { guidanceFor } from "../play/guidance";
import { prospectOf } from "../play/prospects";
import { remainingTally } from "../play/remaining";
import { rulesFrom } from "../play/rules";
import { liftedIdentifier } from "../play/selection";
import type { StoryKind } from "../play/story";
import { storyFor } from "../play/story";
import { tintFor } from "../play/tints";
import { trayTilesOf } from "../play/tray";
import { useAlerts } from "../play/useAlerts";
import { useCountdown } from "../play/useCountdown";
import { useDescription } from "../play/useDescription";
import { useDesk } from "../play/useDesk";
import { usePlay } from "../play/usePlay";
import type { Arrival } from "../play/useStanding";
import type { TileBindings } from "./bindings";
import { BlankPicker } from "./BlankPicker";
import { Board } from "./Board";
import { Controls } from "./Controls";
import type { Carry, DeskSpot, Grasp, GraspSession } from "./dragging";
import { carriedTo, isCarry } from "./dragging";
import { GameOver } from "./GameOver";
import type { KeyHandlers } from "./keys";
import { boundKeys } from "./keys";
import { ModeToggle } from "./ModeToggle";
import { MoveLog } from "./MoveLog";
import { Plaques } from "./Plaques";
import { Rack } from "./Rack";
import { RemainingTiles } from "./RemainingTiles";
import { Room } from "./Room";
import type { StatusTone } from "./StatusLine";
import { StatusLine } from "./StatusLine";
import {
    bagCaption,
    captionFor,
    clockCaption,
    CONNECTION_CAPTIONS,
    exchangeCaption,
    exchangeGuidance,
    guidanceCaption,
    primaryCaption,
    PRODUCT_NAME,
    STALE_NOTICE,
} from "./strings";
import type { DropTarget } from "./targets";
import { targetsFrom } from "./targets";
import { TileFace } from "./TileFace";
import { Tray } from "./Tray";
import { Words } from "./Words";

export interface TableProps {
    readonly arrival: Arrival;
    readonly connection: Connection;
    readonly state: TableState;
    readonly clock: ClockView | null;
    readonly trouble: string | null;
    readonly onOutdated: () => void;
}

interface BlankChoice {
    readonly cell: number;
    readonly tile: Tile;
}

export function Table({ arrival, connection, state, clock, trouble, onOutdated }: TableProps): ReactElement {
    const mySeat = arrival.seated ?? seatedAs(state.view);
    const description = useDescription(arrival.seat);
    const remaining = useCountdown(clock);

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

    const { desk, perform: performDesk } = useDesk(state, mySeat, arrival.seat, atDesk);
    const { busy, notice, noticeCode, send, clear } = usePlay(arrival.seat, state.seq, onOutdated);
    const perform = (effect: DeskEffect): void => {
        clear();
        performDesk(effect);
    };
    const [blankChoice, setBlankChoice] = useState<BlankChoice | null>(null);
    useAlerts(story.kind === "acting", PRODUCT_NAME);

    const lastPlay = state.view.last_play;
    const freshCells = new Set(lastPlay?.indices ?? []);
    const freshTint = lastPlay === null ? null : tintFor(lastPlay.player).hex;
    const countdown =
        clock === null || remaining === null || state.view.phase !== "turn"
            ? null
            : {
                  seat: clock.seat,
                  caption: clockCaption(remaining),
                  urgency: urgencyOf(remaining, clock.per_turn_seconds),
              };
    const tally = description === null ? null : remainingTally(description, state.view.board, rack);

    const prospect = prospectOf(state.view.board, desk.draft, rules);
    const heldBack = draftedIdentifiers(desk.draft);
    const parked = new Set(desk.tray);
    const arranged = rack === null ? [] : arrangedTiles(desk.arrangement, rack);
    const rackRow = arranged.filter((tile) => !heldBack.has(tile.identifier) && !parked.has(tile.identifier));
    const trayRow = rack === null ? [] : trayTilesOf(desk.tray, rack);

    const exchanging = desk.draft.length === 0 && desk.tray.length > 0;
    const exchange = mySeat === null ? null : exchangeProspectOf(desk.tray.length, state.view, mySeat, rules);
    const playArmed = mayAct && prospect.verdict === "playable";
    const primaryArmed = exchanging ? mayAct && (exchange?.allowed ?? false) : playArmed;

    const invalidTexts = invalidTextsOf(noticeCode, notice);
    const chips = prospect.words.map((word) => ({
        ...word,
        status: wordStatusFor(rules.feedback, word.text, invalidTexts),
    }));
    const shownNotice = noticeCode === STALE_POSITION_CODE ? STALE_NOTICE : notice;
    const guidance =
        shownNotice ??
        (exchanging && exchange !== null
            ? exchangeGuidance(exchange.block, exchange.remaining, rules.exchangeMinBag)
            : guidanceCaption(guidanceFor(prospect.verdict, desk.lift !== null)));

    const lay = (cell: number, tile: Tile): void => {
        if (!mayAct || state.view.board.tiles[cell] !== null) {
            return;
        }
        if (tile.blank) {
            setBlankChoice({ cell, tile });
            return;
        }
        perform({ kind: "lay", cell, tile, letter: null });
    };
    const layLifted = (cell: number): void => {
        if (desk.lift !== null) {
            lay(cell, desk.lift.tile);
        }
    };
    const pick = (symbol: string): void => {
        if (blankChoice !== null) {
            perform({ kind: "lay", cell: blankChoice.cell, tile: blankChoice.tile, letter: symbol });
        }
        setBlankChoice(null);
    };
    const primary = (): void => {
        if (!primaryArmed || busy || mySeat === null) {
            return;
        }
        if (exchanging) {
            send(exchangeMove(mySeat, desk.tray), asPremove);
            return;
        }
        send(playMove(mySeat, placementsOf(desk.draft, state.view.board.size)), asPremove);
    };
    const pass = (): void => {
        if (mayAct && !busy) {
            send(passMove(mySeat), asPremove);
        }
    };
    const shuffle = (): void => {
        const visible = new Set(rackRow.map((tile) => tile.identifier));
        perform({ kind: "arrange", arrangement: shuffledArrangement(desk.arrangement, visible, Math.random) });
    };
    const retreat = (): void => {
        if (blankChoice !== null) {
            setBlankChoice(null);
            return;
        }
        perform({ kind: desk.lift !== null ? "clear-lift" : "recall" });
    };

    const tap = (grasp: Grasp): void => {
        perform(tapEffect(desk.lift, grasp));
    };
    const drop = (grasp: Grasp, target: DropTarget | null): void => {
        for (const effect of dropEffects(grasp, target, mayAct)) {
            perform(effect);
        }
        if (target?.kind === "cell" && grasp.spot.kind !== "cell" && grasp.tile.blank) {
            if (mayAct && state.view.board.tiles[target.cell] === null) {
                setBlankChoice({ cell: target.cell, tile: grasp.tile });
            }
        }
    };

    const rootRef = useRef<HTMLDivElement | null>(null);
    const sessionRef = useRef<GraspSession | null>(null);
    const [carry, setCarry] = useState<Carry | null>(null);
    const bindings: TileBindings = {
        onTap: tap,
        onDown: (grasp, event): void => {
            if (rootRef.current === null) {
                return;
            }
            event.currentTarget.setPointerCapture(event.pointerId);
            sessionRef.current = {
                grasp,
                start: { x: event.clientX, y: event.clientY },
                touch: event.pointerType === "touch",
                targets: targetsFrom(rootRef.current, state.view.board.size),
                carrying: false,
            };
        },
        onMove: (event): void => {
            const session = sessionRef.current;
            if (session === null) {
                return;
            }
            const point = { x: event.clientX, y: event.clientY };
            if (!session.carrying && isCarry(session.start, point)) {
                session.carrying = true;
            }
            if (session.carrying) {
                setCarry(carriedTo(session, point));
            }
        },
        onUp: (event): void => {
            const session = sessionRef.current;
            sessionRef.current = null;
            setCarry(null);
            if (session === null) {
                return;
            }
            if (session.carrying) {
                drop(session.grasp, carriedTo(session, { x: event.clientX, y: event.clientY }).target);
                return;
            }
            tap(session.grasp);
        },
        onCancel: (): void => {
            sessionRef.current = null;
            setCarry(null);
        },
    };

    const keysRef = useRef<KeyHandlers>({ onEscape: () => undefined, onEnter: () => undefined });
    useEffect(() => {
        keysRef.current = { onEscape: retreat, onEnter: primary };
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
        <div ref={rootRef} className="table" data-acting={story.kind === "acting" ? "true" : undefined} style={style}>
            <header className="status-strip">
                <StatusLine text={captionFor(story, state.company)} tone={toneOf(story.kind)} />
                <span className="status-meta">{bagCaption(state.view.bag_count)}</span>
                {description !== null && description.code !== null ? (
                    <span className="status-code">{description.code}</span>
                ) : null}
                {connection === "live" ? null : (
                    <span className="chip chip-connection" data-connection={connection}>
                        {CONNECTION_CAPTIONS[connection]}
                    </span>
                )}
                <ModeToggle />
            </header>
            <Plaques view={state.view} company={state.company} mySeat={mySeat} countdown={countdown} />
            <div className="board-region">
                <Board
                    board={state.view.board}
                    pending={pendingFacesOf(desk.draft)}
                    targeting={mayAct && desk.lift !== null}
                    dropCell={carry?.target?.kind === "cell" ? carry.target.cell : null}
                    fresh={freshCells}
                    freshTint={freshTint}
                    onLay={mayAct ? layLifted : null}
                    bindings={atDesk ? bindings : null}
                />
            </div>
            <div className="side">
                {gathering ? (
                    <Room
                        table={arrival.seat.table}
                        code={arrival.code}
                        present={present}
                        total={state.company.seats.length}
                    />
                ) : null}
                {atDesk ? (
                    <div className="feedback">
                        {shownNotice === null && chips.length > 0 ? (
                            <Words chips={chips} bingo={prospect.bingo ? rules.bingoBonus : 0} />
                        ) : (
                            <p className="guidance" role="status" data-tone={shownNotice !== null ? "danger" : "hint"}>
                                {guidance}
                            </p>
                        )}
                    </div>
                ) : null}
                {atDesk ? (
                    <>
                        <Rack
                            tiles={rackRow}
                            capacity={rules.rackSize ?? rackRow.length}
                            liftedId={liftedIdentifier(desk.lift)}
                            bindings={bindings}
                            returnable={desk.lift !== null && desk.lift.from === "tray"}
                            onReturn={(): void => {
                                if (desk.lift !== null) {
                                    perform({ kind: "retrieve", id: desk.lift.tile.identifier, before: null });
                                }
                            }}
                        />
                        <Tray
                            tiles={trayRow}
                            liftedId={liftedIdentifier(desk.lift)}
                            bindings={bindings}
                            parkable={desk.lift !== null && desk.lift.from === "rack"}
                            onPark={(): void => {
                                if (desk.lift !== null) {
                                    perform({ kind: "park", id: desk.lift.tile.identifier, before: null });
                                }
                            }}
                        />
                        <Controls
                            caption={
                                exchanging
                                    ? exchangeCaption(desk.tray.length)
                                    : primaryCaption(asPremove, playArmed ? prospect.points : null)
                            }
                            armed={primaryArmed}
                            premove={asPremove}
                            busy={busy}
                            canRecall={desk.draft.length > 0 || desk.lift !== null}
                            canShuffle={rackRow.length > 1}
                            canPass={mayAct && rules.passAllowed}
                            onPrimary={primary}
                            onRecall={(): void => {
                                perform({ kind: "recall" });
                            }}
                            onShuffle={shuffle}
                            onPass={pass}
                        />
                    </>
                ) : rack !== null && rack.length > 0 ? (
                    <Rack
                        tiles={rack}
                        capacity={rules.rackSize ?? rack.length}
                        liftedId={null}
                        bindings={null}
                        returnable={false}
                        onReturn={() => undefined}
                    />
                ) : null}
                {gathering ? null : (
                    <div className="docket">
                        <MoveLog log={state.log} company={state.company} />
                        {tally === null ? null : <RemainingTiles tally={tally} />}
                    </div>
                )}
                {trouble !== null && connection !== "live" ? <p className="trouble">{trouble}</p> : null}
            </div>
            {carry === null ? null : (
                <div
                    className="carry-ghost"
                    data-touch={carry.touch ? "true" : undefined}
                    style={{ "--carry-x": `${String(carry.point.x)}px`, "--carry-y": `${String(carry.point.y)}px` }}
                >
                    <TileFace tile={carry.tile} />
                </div>
            )}
            {blankChoice !== null ? (
                <BlankPicker
                    alphabet={rules.alphabet}
                    onPick={pick}
                    onClose={(): void => {
                        setBlankChoice(null);
                    }}
                />
            ) : null}
            {story.kind === "over" ? <GameOver view={state.view} company={state.company} story={story} /> : null}
        </div>
    );
}

function tapEffect(lift: { readonly tile: Tile; readonly from: "rack" | "tray" } | null, grasp: Grasp): DeskEffect {
    if (grasp.spot.kind === "cell") {
        return { kind: "take-back", cell: grasp.spot.cell };
    }
    if (grasp.spot.kind === "rack") {
        if (lift !== null && lift.from === "tray" && lift.tile.identifier !== grasp.tile.identifier) {
            return { kind: "retrieve", id: lift.tile.identifier, before: grasp.tile.identifier };
        }
        return { kind: "lift", tile: grasp.tile, from: "rack" };
    }
    if (lift !== null && lift.from === "rack" && lift.tile.identifier !== grasp.tile.identifier) {
        return { kind: "park", id: lift.tile.identifier, before: grasp.tile.identifier };
    }
    return { kind: "lift", tile: grasp.tile, from: "tray" };
}

function dropEffects(grasp: Grasp, target: DropTarget | null, mayAct: boolean): readonly DeskEffect[] {
    if (target === null) {
        return grasp.spot.kind === "cell" ? [{ kind: "take-back", cell: grasp.spot.cell }] : [];
    }
    if (target.kind === "cell") {
        return cellDropEffects(grasp, target.cell, mayAct);
    }
    if (target.kind === "rack") {
        return rackDropEffects(grasp.spot, grasp.tile, target.before);
    }
    return trayDropEffects(grasp.spot, grasp.tile, target.before);
}

function cellDropEffects(grasp: Grasp, cell: number, mayAct: boolean): readonly DeskEffect[] {
    if (!mayAct) {
        return [];
    }
    if (grasp.spot.kind === "cell") {
        return grasp.spot.cell === cell ? [] : [{ kind: "relay", from: grasp.spot.cell, to: cell }];
    }
    if (grasp.tile.blank) {
        return [];
    }
    return [{ kind: "lay", cell, tile: grasp.tile, letter: null }];
}

function rackDropEffects(spot: DeskSpot, tile: Tile, before: number | null): readonly DeskEffect[] {
    if (spot.kind === "cell") {
        return [
            { kind: "take-back", cell: spot.cell },
            { kind: "reorder", id: tile.identifier, before },
        ];
    }
    if (spot.kind === "tray") {
        return [{ kind: "retrieve", id: tile.identifier, before }];
    }
    return [{ kind: "reorder", id: tile.identifier, before }];
}

function trayDropEffects(spot: DeskSpot, tile: Tile, before: number | null): readonly DeskEffect[] {
    if (spot.kind === "cell") {
        return [
            { kind: "take-back", cell: spot.cell },
            { kind: "park", id: tile.identifier, before },
        ];
    }
    return [{ kind: "park", id: tile.identifier, before }];
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
