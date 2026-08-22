import type { CSSProperties, PointerEvent as ReactPointerEvent, ReactElement } from "react";
import { useEffect, useRef, useState } from "react";

import { exchangeMove, passMove, playMove } from "../api/moves";
import { STALE_POSITION_CODE } from "../api/refusal";
import type { ClockView, CompanyView, Tile } from "../api/views";
import type { Incoming, Landing, RowRegion } from "../play/board/landing";
import { incomingOf } from "../play/board/landing";
import { prospectOf } from "../play/board/prospects";
import type { DeskSpot } from "../play/board/spot";
import { standingWordsAt } from "../play/board/standing";
import { outOfTime } from "../play/clock/budget";
import { remainingFor, urgencyOf } from "../play/clock/clock";
import { useCountdown } from "../play/clock/useCountdown";
import { useAlerts } from "../play/device/useAlerts";
import type { Connection } from "../play/live/connection";
import type { TableState } from "../play/live/events";
import { seatedAs } from "../play/live/events";
import { rulesFrom } from "../play/live/rules";
import { useDescription } from "../play/live/useDescription";
import { usePlay } from "../play/live/usePlay";
import { useLore } from "../play/lore/useLore";
import { tintFor } from "../play/seats/tints";
import type { Arrival } from "../play/seats/useStanding";
import { useSettings } from "../play/settings/useSettings";
import { guidanceFor } from "../play/story/guidance";
import { remainingTally } from "../play/story/remaining";
import type { StoryKind } from "../play/story/story";
import { storyFor } from "../play/story/story";
import { useFreshPlay } from "../play/story/useFreshPlay";
import { useHighlights } from "../play/story/useHighlights";
import { arrangedTiles, shuffledArrangement } from "../play/tiles/arrangement";
import type { DeskEffect } from "../play/tiles/desk";
import type { Draft } from "../play/tiles/draft";
import { draftedIdentifiers, pendingAt, placementsOf, shownTile } from "../play/tiles/draft";
import { exchangeProspectOf } from "../play/tiles/exchange";
import { blankLanding, dropEffects, tapEffects } from "../play/tiles/gestures";
import { NO_COMMITTED_TILES, queuedPremoveOf, returnedPremoveOf } from "../play/tiles/premoves";
import { liftedIdentifier } from "../play/tiles/selection";
import { trayTilesOf } from "../play/tiles/tray";
import { useDesk } from "../play/tiles/useDesk";
import { askedPlayed, askedStanding } from "../play/words/asked";
import { invalidTextsOf, wordStatusFor } from "../play/words/feedback";
import { askedWord, panelStanding } from "../play/words/panel";
import { useJudgements } from "../play/words/useJudgements";
import { useWordPanel } from "../play/words/useWordPanel";
import { Board } from "./board/Board";
import { BoardStage } from "./board/BoardStage";
import { MoveLog } from "./docket/MoveLog";
import { RemainingTiles } from "./docket/RemainingTiles";
import { Controls } from "./hand/Controls";
import { Rack } from "./hand/Rack";
import { Tray } from "./hand/Tray";
import type { TileBindings } from "./input/bindings";
import type { Carry, DragPoint, Grasp, GraspSession } from "./input/dragging";
import { carriedTo, crowded, isCarry } from "./input/dragging";
import type { KeyHandlers } from "./input/keys";
import { boundKeys } from "./input/keys";
import { targetsFrom } from "./input/targets";
import { useHold } from "./input/useHold";
import { MenuButton } from "./menu/MenuButton";
import { TableMenu } from "./menu/TableMenu";
import type { SeatClock } from "./seats/Plaques";
import { Plaques } from "./seats/Plaques";
import { Room } from "./seats/Room";
import type { StatusTone } from "./seats/StatusLine";
import { StatusLine } from "./seats/StatusLine";
import { BlankPicker } from "./sheets/BlankPicker";
import { GameOver } from "./sheets/GameOver";
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
    YOUR_TURN_CAPTION,
} from "./strings";
import { TileFace } from "./tiles/TileFace";
import { WordPanel } from "./words/WordPanel";
import { Words } from "./words/Words";

export interface TableProps {
    readonly arrival: Arrival;
    readonly connection: Connection;
    readonly state: TableState;
    readonly clock: ClockView | null;
    readonly trouble: string | null;
    readonly onOutdated: () => Promise<number | null>;
    readonly onLeave: () => void;
}

interface BlankChoice {
    readonly cell: number;
    readonly tile: Tile;
}

export function Table({ arrival, connection, state, clock, trouble, onOutdated, onLeave }: TableProps): ReactElement {
    const { settings } = useSettings();
    const mySeat = arrival.seated ?? seatedAs(state.view);
    const description = useDescription(arrival.seat);
    const remaining = useCountdown(clock);
    const highlights = useHighlights(arrival.seat, state.view.phase === "game_over");

    const story = storyFor(state.view, state.company, mySeat);
    const present = state.company.seats.filter((seated) => seated.claimed).length;
    const gathering = present < state.company.seats.length;
    const rack = mySeat === null ? null : (state.view.racks[String(mySeat)] ?? null);
    const style: CSSProperties = mySeat === null ? {} : { "--tint": tintFor(mySeat).hex };

    const rules = rulesFrom(description);
    const acting = mySeat !== null && state.view.to_act.includes(mySeat);
    const asPremove = !acting && rules.premovesAllowed;
    const atDesk = mySeat !== null && rack !== null && !gathering && state.view.phase === "turn";
    const ranOut = outOfTime(clock, mySeat, remaining);
    const inPlay = atDesk && !ranOut;
    const mayAct = inPlay && (acting || rules.premovesAllowed);

    const { desk, perform: performDesk } = useDesk(state, mySeat, arrival.seat, inPlay);
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
    const lastPlay = state.view.last_play;
    const {
        marks: fresh,
        frame: freshFrame,
        waving: freshWaving,
        acknowledge: noticeLastPlay,
    } = useFreshPlay(lastPlay, mySeat, state.view.board.size);
    const perform = (effect: DeskEffect): void => {
        clear();
        dismissReturned();
        noticeLastPlay();
        performDesk(effect);
    };
    const [blankChoice, setBlankChoice] = useState<BlankChoice | null>(null);
    const [standingShown, setStandingShown] = useState(true);
    const [menuShown, setMenuShown] = useState(false);
    const {
        panel,
        open: openPanel,
        choose: choosePanel,
        deepen: deepenPanel,
        retreat: retreatPanel,
        close: closePanel,
    } = useWordPanel();
    const asked = askedWord(panel);
    const loreAnswer = useLore(asked);
    const hold = useHold(
        rules.lore
            ? (cell: number): void => {
                  openPanel(standingWordsAt(state.view.board, cell).map((word) => askedStanding(word.text)));
              }
            : null,
    );
    useAlerts(story.kind === "acting", PRODUCT_NAME, settings.notices, YOUR_TURN_CAPTION);

    const freshTint = lastPlay === null ? null : tintFor(lastPlay.player).hex;
    const clocks = seatClocks(state.company, clock, remaining, state.view.phase === "turn");
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
    const primaryArmed = (exchanging ? mayAct && (exchange?.allowed ?? false) : playArmed) && !panelStanding(panel);

    const invalidTexts = invalidTextsOf(noticeCode, notice);
    const judged = useJudgements(
        arrival.seat,
        prospect.words.map((word) => word.text),
        rules.feedback === "live" && blankChoice === null && !panelStanding(panel),
    );
    const chips = prospect.words.map((word) => ({
        ...word,
        status: wordStatusFor(rules.feedback, word.text, invalidTexts, judged),
    }));
    const shownNotice = noticeCode === STALE_POSITION_CODE ? STALE_NOTICE : notice;
    const offline = connection === "live" ? null : trouble;
    const hint = ranOut
        ? guidanceCaption("out-of-time")
        : exchanging && exchange !== null
          ? exchangeGuidance(exchange.block, exchange.remaining, rules.exchangeMinBag)
          : guidanceCaption(guidanceFor(prospect.verdict, desk.lift !== null));
    const feedback = (): ReactElement => {
        if (shownNotice !== null) {
            return danger(shownNotice);
        }
        if (chips.length > 0) {
            return (
                <Words
                    chips={chips}
                    bingo={prospect.bingo ? rules.bingoBonus : 0}
                    openText={asked?.text ?? null}
                    onOpen={
                        rules.lore
                            ? (chip): void => {
                                  openPanel([chip]);
                              }
                            : null
                    }
                />
            );
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
        if (offline !== null) {
            return danger(offline);
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
        if (story.kind === "over" && standingShown) {
            setStandingShown(false);
            return;
        }
        if (menuShown) {
            setMenuShown(false);
            return;
        }
        if (blankChoice !== null) {
            dismissBlank();
            return;
        }
        if (panelStanding(panel)) {
            retreatPanel();
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
    const carryOn = (point: DragPoint): void => {
        const session = sessionRef.current;
        if (session === null) {
            return;
        }
        if (!session.carrying && isCarry(session.start, point)) {
            session.carrying = true;
        }
        if (session.carrying) {
            setCarry(carriedTo(session, point));
        }
    };
    const travel = (event: ReactPointerEvent<HTMLDivElement>): void => {
        const point = { x: event.clientX, y: event.clientY };
        hold?.travelled(point);
        carryOn(point);
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
    const pointersRef = useRef<Set<number>>(new Set());
    const arrive = (event: ReactPointerEvent<HTMLDivElement>): void => {
        pointersRef.current.add(event.pointerId);
        if (crowded(pointersRef.current)) {
            abandon();
            hold?.release();
        }
    };
    const depart = (event: ReactPointerEvent<HTMLDivElement>): void => {
        pointersRef.current.delete(event.pointerId);
    };
    const settle = (event: ReactPointerEvent<HTMLDivElement>): void => {
        depart(event);
        release(event);
    };
    const forsake = (event: ReactPointerEvent<HTMLDivElement>): void => {
        depart(event);
        abandon();
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
            onPointerDown={arrive}
            onPointerMove={travel}
            onPointerUp={settle}
            onPointerCancel={forsake}
        >
            <header className="status-strip">
                <StatusLine
                    text={captionFor(story, state.company)}
                    tone={toneOf(story.kind)}
                    onOpen={
                        story.kind === "over" && !standingShown
                            ? (): void => {
                                  setStandingShown(true);
                              }
                            : null
                    }
                />
                {story.kind === "over" ? null : <span className="status-meta">{bagCaption(state.view.bag_count)}</span>}
                {connection === "live" ? null : (
                    <span className="chip chip-connection" data-connection={connection}>
                        {CONNECTION_CAPTIONS[connection]}
                    </span>
                )}
                <MenuButton
                    onOpen={(): void => {
                        setMenuShown(true);
                    }}
                />
            </header>
            <Plaques
                view={state.view}
                company={state.company}
                mySeat={mySeat}
                clocks={clocks}
                clocked={clock !== null}
            />
            <div className="board-region" onPointerDown={noticeLastPlay}>
                <BoardStage onZoom={noticeLastPlay}>
                    <Board
                        board={state.view.board}
                        pending={pendingFacesOf(desk.draft)}
                        ghosts={ghosts}
                        targeting={mayAct && desk.lift !== null}
                        dropCell={
                            carry?.target?.kind === "cell" && !ghosts.has(carry.target.cell) ? carry.target.cell : null
                        }
                        fresh={fresh}
                        freshFrame={freshFrame}
                        freshTint={freshTint}
                        freshWaving={freshWaving}
                        onLay={mayAct ? layLifted : null}
                        bindings={atDesk ? bindings : null}
                        hold={hold}
                    />
                </BoardStage>
            </div>
            <div className="side">
                {gathering ? <Room code={arrival.code} present={present} total={state.company.seats.length} /> : null}
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
                            canPass={acting && rules.passAllowed && !ranOut}
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
                        <MoveLog
                            log={state.log}
                            company={state.company}
                            onOpen={
                                rules.lore
                                    ? (word): void => {
                                          openPanel([askedPlayed(word)]);
                                      }
                                    : null
                            }
                        />
                        {tally === null ? null : <RemainingTiles tally={tally} />}
                    </div>
                )}
                {atDesk || offline === null ? null : <p className="trouble">{offline}</p>}
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
            {menuShown ? (
                <TableMenu
                    code={arrival.code}
                    onLeave={onLeave}
                    onClose={(): void => {
                        setMenuShown(false);
                    }}
                />
            ) : null}
            {blankChoice !== null ? (
                <BlankPicker alphabet={rules.alphabet} onPick={pick} onClose={dismissBlank} />
            ) : null}
            {asked === null ? null : (
                <WordPanel
                    asked={asked}
                    words={panel.words}
                    chosen={panel.chosen}
                    answer={loreAnswer}
                    lexeme={panel.lexeme}
                    onChoose={choosePanel}
                    onDeepen={deepenPanel}
                    onRetreat={retreatPanel}
                    onClose={closePanel}
                />
            )}
            {story.kind === "over" && standingShown ? (
                <GameOver
                    view={state.view}
                    company={state.company}
                    story={story}
                    highlights={highlights}
                    mySeat={mySeat}
                    onClose={(): void => {
                        setStandingShown(false);
                    }}
                    onLeave={onLeave}
                />
            ) : null}
        </div>
    );
}

function seatClocks(
    company: CompanyView,
    clock: ClockView | null,
    running: number | null,
    playing: boolean,
): ReadonlyMap<number, SeatClock> {
    const clocks = new Map<number, SeatClock>();
    if (clock === null || !playing) {
        return clocks;
    }
    for (const seated of company.seats) {
        const seconds = remainingFor(clock, seated.seat, running);
        if (seconds !== null) {
            clocks.set(seated.seat, { caption: clockCaption(seconds), urgency: urgencyOf(seconds) });
        }
    }
    return clocks;
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
