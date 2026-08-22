# Architecture

_Słowiki_ follows the CardWork architecture: a pure, synchronous game core
surrounded by a transport adapter, game presets, a dictionary subproject, and a
composition root.

## Principles

P1. The core is a pure function of the position: `apply(position, move) -> position`.
    Every rule is a pure function of the position it receives.

P2. Randomness is recorded. The bag shuffle is a permutation stored in the
    initial position, so a game replays deterministically.

P3. The board is mechanism, rules are policy. The board stores squares and
    bonuses; the scoring and validity kernel interprets them.

P4. Only projections cross the wire. The server derives a per-observer view and
    hides racks and premoves of other seats.

P5. The journal is append-only. Each move appends a transaction of the form
    `(sequence, move, resulting_position)`.

P6. The engine owns the cursor. Turn order, phase, and premove settlement are
    engine concerns; game rules supply validation and application. The session
    decides when a queued premove settles, the way it already owns the wall clock.

P7. Letters are canonical. Every letter inside the system is uppercase; dictionary
    loaders, tile presets, and move payloads normalize on ingestion, so rules,
    scoring, and projections compare letters directly. Compiled lexicons carry a
    format version (`LEXICON_FORMAT` in `wordtable.paths`), so a normalization
    change retires stale artifacts by filename.

## Packages

- `wordcore` — the engine: frozen models, tiles, board, moves, rules kernel,
  lexicon protocol, projections, and the game runner.
- `wordgames` — game presets: shared rules and the literaki/scrabble backends.
- `wordserver` — the FastAPI adapter: tables, sessions, SSE, identity, time.
- `wordtable` — configuration, paths, lexicon service, and CLI entry points.
- `lexica` — dictionary building: word entries, SJP loader, compilation, and
  the morphology pipeline (`docs/morphology.md`, `docs/morphology-pipeline.md`).
- `wordbots` — automated player stubs.
- `wordassets` — asset generation: an SVG element tree, board specimens, and the
  build CLI writing gitignored `assets/` plus committed specimen copies in
  `docs/media/`.

## Module layout

Each module holds one concept; shared models and enums live in modules named
after them (`board.bonus`, `moves.kind`, `moves.move`, `games.kind`,
`games.rules`, `lexicon.protocol`, `lexicon.verdict`). The rules kernel splits
into `wordcore.rules.words` (placements and word geometry) and
`wordcore.rules.score` (word and move scoring). Dictionary source loaders live
under `lexica.dictionaries`, one module per source.

## Frontend

The player interface lives in `frontend/` and splits into two strata: one reasons about the game on
the client — state derivation, board geometry, score previews, session and device concerns — and one
presents it. Its types come from the server's OpenAPI document, so the wire contract is generated
rather than restated. `docs/frontend.md` holds the code principles; `docs/interface.md` holds the
design contract.

## Vocabulary

- `wordgames.names.GameName` — literaki, scrabble.
- `lexica.names.DictionaryName` — sjp, english, osps.
- `wordcore.moves.kind.ActionKind` — play, exchange, pass.
- `wordcore.games.kind.EntryKind` — move, premove_set, premove_cleared,
  premove_discarded.

## HTTP surface

- `GET /offerings` — schemes whose dictionaries are present on disk.
- `GET /style` — the design tokens for the active theme, asked once per client.
- `POST /tables`, `POST /tables/{code}/join` — admissions with seat tokens.
- `GET /tables/{table_id}` — the table description: rules parameters, alphabet,
  distribution, and the join code for seat holders.
- `GET /tables/{table_id}/view` — the per-observer projection with the company
  and the turn clock.
- `GET /tables/{table_id}/words` — dictionary verdicts for up to sixteen words,
  offered while the scheme validates on play (`parameters.word_check`).
- `GET /tables/{table_id}/highlights` — the highest-scoring word and the longest
  word of the game, walked from the journal, so the answer stays whole however
  late a client connects.
- `POST /tables/{table_id}/moves`, `DELETE /tables/{table_id}/premove` — play.
- `PUT /tables/{table_id}/rack` — the order the seat keeps its own letters in.
- `GET /tables/{table_id}/events` — the SSE stream: numbered journal frames plus
  unnumbered `presence`, `position`, `clock` and `heartbeat` frames. A stream opens
  by stating the observer's whole standing — the company, the observer's own
  projection, and the turn clock — and a `position` frame follows whenever that
  projection changes for a reason the journal does not record, so the letters ride
  the wakeup that carries the turn. A quiet table sends a `heartbeat` carrying the
  server's clock every fifteen seconds, so a client reads liveness from the stream
  itself and treats silence past two beats as a dropped connection.
- `/artwork` — the generated asset tree (icons, brand art, board specimens);
  `/favicon.ico` serves from it.

## Clocks

Wall-clock time is session state, never position state. `TurnClock`
(`wordserver/clocks.py`) holds what each seat has left and the deadline of the
seat on turn: arming a turn takes the shorter of the scheme's per-turn budget and
the seat's own remaining time, settling a turn charges the thinking time and adds
the increment after a play or an exchange. A seat whose budget is spent leaves the
game as an observer: the session refuses every move it submits, discards any premove
it left standing, and auto-passes on its turn, so the opponents play on and the
scheme's end limit closes the game. A queued premove settles
`premove_delay_seconds` after the turn opens, so the move that answered it stands
alone on its own frame first; the seat on turn is already armed, so its clock pays
for the pause. A table asks for its own control at creation (`TableRequest.time`),
which replaces the scheme's default and rides in the description as
`parameters.time`.

## Rack order

The order a seat keeps its letters in is session state, never position state.
`RackOrder` (`wordserver/racks.py`) holds the identifiers each seat last asked
for and lays that seat's own rack out in them whenever the session projects it,
with freshly drawn tiles standing at the end. `PUT /tables/{table_id}/rack`
records an order and stops there, so a player who reloads finds their hand as
they left it while the journal and every other seat read exactly as before.

## Concurrency

The server runs on a single asyncio event loop. Per-table state is guarded by an
`asyncio.Condition` inside `TableSession`; HTTP handlers await, turn timers use
`asyncio.sleep`, and SSE streams wait on the condition. A stream looks for fresh
frames and waits for the next notification inside one critical section, so a frame
committed while a stream settles into its wait reaches that stream at once. A
stream counts itself in and out of the company synchronously and announces the
change under a shield, so a cancelled stream leaves no seat reading as connected.
Dictionary compilation and loading run through `asyncio.to_thread` inside the
`LexiconService`, so the event loop never blocks on disk or CPU-heavy lexicon work.

## Import contracts

`lint-imports` enforces four contracts: the core knows no subsystem, rules are
transport-free, the pure layers reach no adapter or host, and the game,
dictionary, and bot layers stay independent.

`wordserver` consumes configuration and composition helpers from `wordtable`;
a stricter host/adapter split, where `wordtable` is the sole composition root,
is a planned refinement.
