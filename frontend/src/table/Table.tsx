import type { CSSProperties, PointerEvent as ReactPointerEvent, ReactElement } from "react";
import { useEffect, useRef, useState } from "react";

import { exchangeMove, passMove, playMove } from "../api/moves";
import { STALE_POSITION_CODE } from "../api/refusal";
import type { ClockView, Tile } from "../api/views";
import { arrangedTiles, shuffledArrangement } from "../play/arrangement";
import { urgencyOf } from "../play/clock";
import type { Connection } from "../play/connection";
import type { DeskEffect } from "../play/desk";
import type { Draft } from "../play/draft";
import { draftedIdentifiers, pendingAt, placementsOf, shownTile } from "../play/draft";
import type { TableState } from "../play/events";
import { seatedAs } from "../play/events";
import { exchangeProspectOf } from "../play/exchange";
import { invalidTextsOf, wordStatusFor } from "../play/feedback";
import { blankLanding, dropEffects, tapEffects } from "../play/gestures";
import { guidanceFor } from "../play/guidance";
import type { Incoming, Landing, RowRegion } from "../play/landing";
import { incomingOf } from "../play/landing";
import { NO_COMMITTED_TILES, queuedPremoveOf, returnedPremoveOf } from "../play/premoves";
import { prospectOf } from "../play/prospects";
import { remainingTally } from "../play/remaining";
import { rulesFrom } from "../play/rules";
import { liftedIdentifier } from "../play/selection";
import type { DeskSpot } from "../play/spot";
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
import { CodeChip } from "./CodeChip";
import { Controls } from "./Controls";
import type { Carry, Grasp, GraspSession } from "./dragging";
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
    CANCEL_PREMOVE,
    captionFor,
    clockCaption,
    CONNECTION_CAPTIONS,
    exchangeCaption,
    exchangeGuidance,
    guidanceCaption,
    premoveReturnedCaption,
    primaryCaption,
    PRODUCT_NAME,
    queuedCaption,
    STALE_NOTICE,
} from "./strings";
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
    readonly onOutdated: () => Promise<number | null>;
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
    const { busy, notice, noticeCode, send, revoke, clear } = usePlay(arrival.seat, state.seq, onOutdated);
    const queued = queuedPremoveOf(state.view, mySeat);
    const ghosts: ReadonlyMap<number, Tile> = new Map((queued?.ghosts ?? []).map((ghost) => [ghost.cell, ghost.tile]));
    const committed = queued?.committed ?? NO_COMMITTED_TILES;
    const ghosted = queued !== null && queued.kind === "play" ? queued.committed : NO_COMMITTED_TILES;
    const returned = returnedPremoveOf(state.log, mySeat);
    const [returnedSeen, setReturnedSeen] = useState(-1);
    const returnedNotice =
        returned !== null && returned.seq > returnedSeen ? premoveReturnedCaption(returned.reason) : null;
    const dismissReturned = (): void => {
        if (returned !== null) {
            setReturnedSeen(returned.seq);
        }
    };
    const perform = (effect: DeskEffect): void => {
        clear();
        dismissReturned();
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
    const rackRow = arranged.filter(
        (tile) => !heldBack.has(tile.identifier) && !parked.has(tile.identifier) && !ghosted.has(tile.identifier),
    );
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
    const hint =
        exchanging && exchange !== null
            ? exchangeGuidance(exchange.block, exchange.remaining, rules.exchangeMinBag)
            : guidanceCaption(guidanceFor(prospect.verdict, desk.lift !== null));
    const feedback = (): ReactElement => {
        if (shownNotice !== null) {
            return danger(shownNotice);
        }
        if (chips.length > 0) {
            return <Words chips={chips} bingo={prospect.bingo ? rules.bingoBonus : 0} />;
        }
        if (returnedNotice !== null) {
            return danger(returnedNotice);
        }
        if (queued !== null) {
            return (
                <div className="queued" role="status">
                    <span className="queued-caption">{queuedCaption(queued.kind)}</span>
                    <button type="button" className="queued-cancel" disabled={busy} onClick={revoke}>
                        {CANCEL_PREMOVE}
                    </button>
                </div>
            );
        }
        return (
            <p className="guidance" role="status" data-tone="hint">
                {hint}
            </p>
        );
    };

    const boardFree = (cell: number): boolean => state.view.board.tiles[cell] === null && !ghosts.has(cell);
    const reached = (landing: Landing | null): Landing | null => {
        if (landing?.kind !== "cell") {
            return landing;
        }
        return boardFree(landing.cell) ? landing : null;
    };
    const land = (spot: DeskSpot, tile: Tile, landing: Landing | null): void => {
        const target = reached(landing);
        for (const effect of dropEffects(spot, tile, target, mayAct)) {
            perform(effect);
        }
        const asking = blankLanding(spot, tile, target);
        if (asking !== null && mayAct && pendingAt(desk.draft, asking) === null) {
            setBlankChoice({ cell: asking, tile });
        }
    };
    const layLifted = (cell: number): void => {
        if (desk.lift !== null) {
            land(desk.lift.from, desk.lift.tile, { kind: "cell", cell });
        }
    };
    const pick = (symbol: string): void => {
        if (blankChoice !== null) {
            perform({ kind: "stamp", cell: blankChoice.cell, letter: symbol });
        }
        setBlankChoice(null);
    };
    const dismissBlank = (): void => {
        if (blankChoice !== null) {
            perform({ kind: "take-back", cell: blankChoice.cell });
            setBlankChoice(null);
        }
    };
    const primary = (): void => {
        if (!primaryArmed || busy || mySeat === null || blankChoice !== null) {
            return;
        }
        dismissReturned();
        if (exchanging) {
            send(exchangeMove(mySeat, desk.tray), asPremove);
            return;
        }
        send(playMove(mySeat, placementsOf(desk.draft, state.view.board.size)), asPremove);
    };
    const pass = (): void => {
        if (acting && !busy) {
            dismissReturned();
            send(passMove(mySeat), false);
        }
    };
    const shuffle = (): void => {
        const visible = new Set(rackRow.map((tile) => tile.identifier));
        perform({ kind: "arrange", arrangement: shuffledArrangement(desk.arrangement, visible, Math.random) });
    };
    const retreat = (): void => {
        if (blankChoice !== null) {
            dismissBlank();
            return;
        }
        perform({ kind: desk.lift !== null ? "clear-lift" : "recall" });
    };

    const tap = (grasp: Grasp): void => {
        for (const effect of tapEffects(desk.lift, grasp.spot, grasp.tile)) {
            perform(effect);
        }
    };

    const rootRef = useRef<HTMLDivElement | null>(null);
    const sessionRef = useRef<GraspSession | null>(null);
    const [carry, setCarry] = useState<Carry | null>(null);
    const bindings: TileBindings = {
        lifted: liftedIdentifier(desk.lift),
        carried: carry?.tile.identifier ?? null,
        onTap: tap,
        onDown: (grasp, event): void => {
            const root = rootRef.current;
            if (root === null) {
                return;
            }
            root.setPointerCapture(event.pointerId);
            sessionRef.current = {
                grasp,
                start: { x: event.clientX, y: event.clientY },
                touch: event.pointerType === "touch",
                targets: targetsFrom(root, state.view.board.size),
                carrying: false,
            };
        },
    };
    const travel = (event: ReactPointerEvent<HTMLDivElement>): void => {
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
    };
    const release = (event: ReactPointerEvent<HTMLDivElement>): void => {
        const session = sessionRef.current;
        sessionRef.current = null;
        setCarry(null);
        if (session === null) {
            return;
        }
        if (session.carrying) {
            land(
                session.grasp.spot,
                session.grasp.tile,
                carriedTo(session, { x: event.clientX, y: event.clientY }).target,
            );
            return;
        }
        tap(session.grasp);
    };
    const abandon = (): void => {
        sessionRef.current = null;
        setCarry(null);
    };

    const incoming = (region: RowRegion): Incoming | null =>
        carry === null ? null : incomingOf(carry.target, carry.tile.identifier, region);

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
        <div
            ref={rootRef}
            className="table"
            data-acting={story.kind === "acting" ? "true" : undefined}
            style={style}
            onPointerMove={travel}
            onPointerUp={release}
            onPointerCancel={abandon}
        >
            <header className="status-strip">
                <StatusLine text={captionFor(story, state.company)} tone={toneOf(story.kind)} />
                <span className="status-meta">{bagCaption(state.view.bag_count)}</span>
                {description !== null && description.code !== null ? <CodeChip code={description.code} /> : null}
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
                    ghosts={ghosts}
                    targeting={mayAct && desk.lift !== null}
                    dropCell={
                        carry?.target?.kind === "cell" && !ghosts.has(carry.target.cell) ? carry.target.cell : null
                    }
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
                {atDesk ? <div className="feedback">{feedback()}</div> : null}
                {atDesk ? (
                    <>
                        <Rack
                            tiles={rackRow}
                            capacity={rules.rackSize ?? rackRow.length}
                            locked={committed}
                            incoming={incoming("rack")}
                            bindings={bindings}
                            returnable={desk.lift !== null && desk.lift.from.kind !== "rack"}
                            onReturn={(): void => {
                                if (desk.lift !== null) {
                                    land(desk.lift.from, desk.lift.tile, { kind: "rack", before: null });
                                }
                            }}
                        />
                        <Tray
                            tiles={trayRow}
                            locked={committed}
                            incoming={incoming("tray")}
                            bindings={bindings}
                            parkable={desk.lift !== null && desk.lift.from.kind !== "tray"}
                            onPark={(): void => {
                                if (desk.lift !== null) {
                                    land(desk.lift.from, desk.lift.tile, { kind: "tray", before: null });
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
                            canPass={acting && rules.passAllowed}
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
                        locked={NO_COMMITTED_TILES}
                        incoming={null}
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
                <BlankPicker alphabet={rules.alphabet} onPick={pick} onClose={dismissBlank} />
            ) : null}
            {story.kind === "over" ? <GameOver view={state.view} company={state.company} story={story} /> : null}
        </div>
    );
}

function pendingFacesOf(draft: Draft): ReadonlyMap<number, Tile> {
    return new Map(draft.map((pending) => [pending.cell, shownTile(pending)]));
}

function danger(text: string): ReactElement {
    return (
        <p className="guidance" role="status" data-tone="danger">
            {text}
        </p>
    );
}

function toneOf(kind: StoryKind): StatusTone {
    if (kind === "acting") {
        return "acting";
    }
    return kind === "over" ? "over" : "quiet";
}
