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
    hides racks and premoves of other seats. What a hidden rack implies and every
    seat is owed travels as its own fact: `out_of_tiles` names the seats holding
    nothing while the bag is empty, so a player watching the turn skip a seat is
    told why.

P5. The journal is append-only. Each move appends a transaction of the form
    `(sequence, move, resulting_position)`.

P6. The engine owns the cursor. Turn order, phase, and premove settlement are
    engine concerns; game rules supply validation and application. The session
    decides when a queued premove settles, the way it already owns the wall clock.
    Ending a game that stands unplayed belongs there too: `Game.abandon` leaves the
    position `unresolved` with the scores the seats have earned, so an award that
    game rules compute stays with the game rules.

P7. Letters are canonical. Every letter inside the system is uppercase; dictionary
    loaders, alphabet presets, and move payloads normalize on ingestion, so rules,
    scoring, and projections compare letters directly. Compiled artifacts carry
    their kind and format version in the header and in the filename
    (`ARTIFACT_FORMATS` in `lexica.artifact.formats`), so a normalization change
    retires stale artifacts and a reader accepts only the kind it understands.
    `docs/lexicon-contract.md` states that boundary between `lexica` and
    `wordtable`, and `make contract` holds the document against the code.

## Packages

- `wordcore` — the engine: frozen models, tiles, board, moves, rules kernel,
  lexicon protocol, projections, and the game runner.
- `wordgames` — rules policy: the word-game backend and the parameters record it
  plays by.
- `wordserver` — the FastAPI adapter: tables, sessions, SSE, identity, time.
- `wordtable` — configuration, paths, lexicon service, and CLI entry points.
- `lexica` — dictionary building: the source loaders, the compiled artifacts,
  the closed Polish grammar vocabulary in `lexica.grammar`, and the readings the
  word panel prints (`docs/lore.md`, `docs/morphology.md`).
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
under `lexica.dictionaries`, one module per source, and each grammar dimension
owns a module under `lexica.grammar`.

Configuration presets own a module each under `wordtable.presets`: the alphabet
(the letters a game plays with, their order, what each class of them is worth,
and the word lists it suits), the distribution (how many tiles of each letter),
a per-letter adjustment, the expansion that settles the three into a
`wordcore.tiles.tileset.TileSet`, and the loaders that read them from disk. They
live beside configuration rather than in the core because an alphabet names the
dictionaries it admits, and the core knows no subsystem. The core holds what the
engine consumes: the settled tile set and the bag built from it.

One record carries the rules. `wordtable.rules.RulesConfig` is flat and complete:
every setting a table may state stands in it, and the record holds their shape —
the types, the canonically uppercase letters, the preset names. A scheme file
(`wordtable.scheme.SchemeConfig`) is an identity plus one such record, and every
rule a record must satisfy is enforced in one place: `wordtable.settling`, whose
`resolve_table` reads as the list it enforces, from the ranges through the
arithmetic to the rules that need the presets. It loads the board, the alphabet
and the distribution, expands the letters, and answers with a
`wordtable.resolved.ResolvedScheme` — the scheme it came from, the rules it plays
by, the board and the settled bag. `resolve_scheme` answers a scheme's own
default; `resolve_table` settles a record onto one.
`wordtable.audit.audit_configuration` walks the whole tree at startup, so a fault
in a preset or a scheme is reported before the service accepts a request — a
preset that is absent, a letter left unvalued, a word list the letters do not
suit, or board art a scheme's own letters cannot spell.

`wordtable.allowances` describes each setting for the interface that renders it:
the group it joins, its tier, the kind of control it takes, the range it stands
inside, and the rungs a picker offers, all authored in `config/allowances.yaml`.
One authored number serves both sides — `wordtable.limits.ensure_within_limits`
holds a record to it at the settling boundary, naming the setting, the range and
the value asked for, and the same number reaches the client that offers it. A row
states a range exactly where its kind takes one, and a test holds each range
against the value a table is held to. The step guides a stepper alone, so a value
between two rungs stands the way an unoffered rung already does. The catalog is
answered whole: what a board, alphabet, distribution or dictionary choice offers
is read from disk, so adding a preset file adds an option.

A scheme's identity is its name and the word its board art paints. One backend
serves every scheme: what distinguishes literaki from scrabble is the board, the
letters and the word list a scheme names, all of them settings, so the rules
class is chosen by nothing and `build_rules` translates the record into
`wordgames.backend.parameters.GameParameters` for it.

## Fixed policy

Seven rules a scheme tunes reach the kernel as keyword-only scalars on pure
functions, the way `validate_exchange` and `validate_words` already took theirs:
how many tiles the opening play takes and whether it covers the center
(`validate_anchor`), how many tiles earn the bingo bonus
(`WordGameRules._bingo_bonus`, where `bingo_tiles` left unstated means the whole
rack), when the game ends (`Ending`, read by `WordGameRules._ending_reached`), and
the three that close it — whether a seat's leftover letters count against it,
whether the seat that goes out takes the opponents' rack totals, and the flat bonus
that seat earns (`final_scores`). `wordcore` stays
configuration-ignorant; `wordgames` holds the only parameters record.

The rest is policy the engine fixes, and this is the whole list:

- Turn order is seat order, and seat 0 moves first.
- A blank is worth nothing and carries the category `blank`, which board art may
  paint and a letter adjustment may not claim. A blank takes any alphabetic
  character as its letter for the play.
- A play takes at least one tile, and tiles adjoin orthogonally.
- A seat goes out by emptying its rack while the bag is empty, and the state
  remembers the first seat to do it. When that ends the game is the table's to
  state: `first_out` closes on the first empty rack, `all_out` plays on past it,
  skipping every seat that is out until the last rack empties. What the closing
  arithmetic makes of it is the table's too: `rack_penalties` deducts each seat's
  remaining rack, `going_out_award` hands those totals to the finisher, and
  `going_out_bonus` pays the finisher a flat sum, which is what still rewards going
  out when the award is off — and under `all_out`, where every rack usually ends
  empty, the flat bonus is the whole of it.
- A one-seat table ends when the seat empties its rack or passes once, whichever
  comes first — the solitaire ending, which a one-seat literaki table inherits.
- `pass_end_rounds` counts rounds, so the limit it sets is
  `pass_end_rounds × seats` consecutive passes.
- An exchange limit counts exchanges rather than tiles, and exchanged tiles
  return to the back of the bag.
- A word is judged or it is not: the table states `validate_on_play`, and there
  is no challenge.
- The bag shuffle draws from an unseeded `random.Random()`, recorded in the
  initial position (P2).
- A board is a preset file: a table picks one, and painting individual squares
  belongs to configuration.

## Frontend

The player interface lives in `frontend/` and splits into two strata: one reasons about the game on
the client — state derivation, board geometry, score previews, session and device concerns — and one
presents it. Its types come from the server's OpenAPI document, so the wire contract is generated
rather than restated. `docs/frontend.md` holds the code principles; `docs/interface.md` holds the
design contract.

## Vocabulary

- `lexica.names.DictionaryName` — sjp, english, osps.
- `wordcore.moves.kind.ActionKind` — play, exchange, pass.
- `wordcore.games.kind.EntryKind` — move, premove_set, premove_cleared,
  premove_discarded, abandoned.
- `wordcore.states.phase.Phase` — turn, game_over, unresolved; `finished` answers
  for the two a game rests in.

## HTTP surface

- `GET /offerings` — schemes whose dictionaries are present on disk, each with its
  own complete rules record; the shape of a join code, so a client parses what a
  player types from the server's own answer; and the allowance for every setting,
  so the client renders a control per setting from server data.
- `GET /presets` — every board, alphabet and distribution on disk, so a client
  composes a letter set it has never seen and prints what the bag would hold.
  Board art belongs to the scheme named after the board, so which specimen a board
  wears is stated rather than left to the order the files are read in.
- `GET /style` — the design tokens for the active theme, asked once per client.
- `POST /tables` — a scheme, a player name, and optionally the whole rules record
  the table plays by; absent, the scheme's own record stands. Every fault in that
  record answers 422: a setting outside its range answers `setting_out_of_range`
  naming the setting and the range, a board, alphabet or distribution the server
  does not hold answers `unknown_preset`, and rules that contradict each other or
  the presets answer `rules_inconsistent`. A body the record's own shape refuses —
  a setting missing or written as the wrong kind of value — answers
  `malformed_request`.
- `POST /tables/{code}/join` — admissions with seat tokens.
- `GET /invitations/{code}` — the settled description behind a join code, with no
  seat token and no code echoed back, so a guest reads the rules before accepting
  them.
- `GET /tables/{table_id}` — the table description: the settled rules record, what
  feedback the table offers, the alphabet and distribution of the settled bag, and
  the join code for seat holders. Every route under a table answers 404
  `unknown_table` for an identifier the server never held and 410 `table_closed`
  for one it has let go, so a client tells a stale link from a typo.
- `GET /tables/{table_id}/view` — the per-observer projection with the company
  and the turn clock.
- `GET /tables/{table_id}/words` — dictionary verdicts for up to sixteen words,
  offered while the table validates on play (`feedback.word_check`).
- `GET /tables/{table_id}/lore` — the readings of up to sixteen words: part of
  speech, base form and whole paradigm per reading, offered while the scheme's
  dictionary carries Polish morphology (`feedback.lore`). `docs/lore.md` holds
  the sources behind it.
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
scheme's end limit closes the game. That pass is the referee's, not the player's:
`Game.adjudicate_pass` records it on the seat's behalf, so a table that bars passing
still advances when a clock runs out. `pass_allowed` governs what a player may choose.
A queued premove settles
`tables.premove_delay_seconds` after the turn opens, so the move that answered it
stands alone on its own frame first; the seat on turn is already armed, so its
clock pays for the pause. That delay is stream policy the host sets, so it stands
beside `tables.sweep_seconds` in `TablesConfig` and reaches a session as its own
value. The budgets are game rules: a table states them in its rules record, and
`wordtable.timing.time_of` derives the `TimeConfig` the clock reads, and the
description carries them in its rules record.

## Rack order

The order a seat keeps its letters in is session state, never position state.
`RackOrder` (`wordserver/racks.py`) holds the identifiers each seat last asked
for and lays that seat's own rack out in them whenever the session projects it,
with freshly drawn tiles standing at the end. `PUT /tables/{table_id}/rack`
records an order and stops there, so a player who reloads finds their hand as
they left it while the journal and every other seat read exactly as before.

## Table life

A table lives as long as its game does. `TableSweep` (`wordserver/sweep.py`) wakes
every `tables.sweep_seconds` and reads each table's `TableStanding` — its age, and
how long its game has been finished — through `fate_of` (`wordserver/lifetime.py`),
which answers keep, abandon, or close. A game still running past
`tables.life_seconds` is abandoned: the session calls `Game.abandon`, which appends
an `abandoned` entry leaving the position `unresolved` with the scores as they
stand. A finished table closes once its standing has been readable for
`tables.linger_seconds`.

Closing is one path, `TableRegistry.close`: it writes a `GameRecord` into the
`GameBook`, drops the table and its join code from the registry, and closes the
session, which cancels the turn and premove timers and ends every open stream. The
book keeps the last `KEPT_GAMES` records, which is how a request for a table the
server has let go answers 410 rather than 404, and each record reaches the log as
it is filed.

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
