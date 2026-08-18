# Interface

The design contract for the player interface. It fixes the layout regions, the gesture and state
vocabulary, and the design tokens; implementation phases build against it, and visual changes start
by amending it. The palette is the *Lniany* proposition chosen from the phase-0 mockup.

## Principles

1. **The board is the hero.** Every other region yields space to a maximally large, always-square
   board, and every region reserves the height its rules demand rather than the height its current
   contents happen to need, so the board keeps one size from the first tile of a turn to the last.
2. **Hue says who; strength says whose turn.** Player tints color chrome: plaques, rings, the frame
   around a fresh play, log entries. The four Literaki categories color tile faces and premium squares. The
   two palettes stay on separate surfaces, and printed values accompany every color.
3. **State over toasts.** Whose turn it is, a queued premove, a staged exchange, a running clock —
   each is a persistent visual state that survives looking away.
4. **May-I-act is set membership.** Actionability derives from `me ∈ to_act`, so several
   simultaneous actors render correctly and a future real-time scheme is a data change.
5. **The page knows no game.** Rack size, exchange limits, premove availability, the feedback
   policy, and the alphabet arrive as data from the table description, and the interface renders
   behavior from them.

## Screens

- **Arrive** — a single card: creating a table (scheme picker bounded by the offering's real
  player range, seat count, and the clock: a time budget per player from one minute to an hour, or
  untimed, beside the bonus added after every play or exchange — one fixed row of two controls, the
  bonus quiet and inert while the table stays untimed, so the card holds its size through every
  choice) and a quiet switch to the join card for holders of a code. An invitation link opens
  straight onto the join card with the code prefilled, and that card keeps the switch, so a guest
  can start a table of their own. The name field persists in local storage across visits.
  Credentials live in the URL fragment; a reload rejoins by token, and while no seat is held the
  page follows the address bar, so an invitation pasted over an idle page opens its join card. A
  held seat keeps its own address.
- **Table** — the one screen where the game lives. Until every seat is claimed it doubles as the
  room: a gathering banner with the join code, a copy-invitation control, and claimed/empty
  plaques.
- **Game over** — the final standing as an overlay: winner, rack deductions, the board still
  readable beneath.

## Table regions

Portrait (primary): status strip → plaques ribbon → board → feedback line → rack → exchange tray
→ controls → docket, inside a `100dvh` grid with safe-area insets and the page scroll locked (the
gesture surface owns every touch; long panels scroll internally). Landscape and desktop reshuffle
grid areas only: the board sits height-bound on the left; the right column stacks status, plaques,
feedback line, rack, tray, controls, and the docket at its foot.

- **Status strip** — turn banner ("Your turn" at accent strength; "Ola is thinking — 1:12" quiet),
  clock, bag count, join-code chip (a click copies the code), connection state, and four quiet
  toggles: the turn notice, the color mode, the interface motion, and the language.
- **Plaques** — one per player, one to eight: tint dot, name, score, acting ring at full tint
  strength that breathes while the seat is on turn, premove diamond, and — on a timed table — a
  clock line under the name: the thinking seat counts down live, everyone else shows the budget
  they have banked, and a seat without a clock of its own holds a dash so the row keeps its height
  through every turn.
- **Board** — 15 × 15 (size is data), premium squares whose `×3` / `2×` / `3×` glyph is printed as
  a watermark of its own fill — legible when read, quiet at a glance — the center star at full
  strength over whatever square it falls on, every tile keeping a margin inside its square so a word
  reads as a row of tiles, the last play framed end to end in the mover's tint and waving until the
  player has seen it, pending tiles raised above their neighbors with a solid accent ring, premove
  ghosts at reduced opacity in the premove accent.
- **Feedback line** — one fixed-height slot showing, in order of precedence: the refusal or
  notice sentence, the formed-word chips (points and status dot each) while a draft stands, the
  returned-premove explanation, the queued-premove chip with its Cancel action, the connection
  trouble sentence, or the guidance hint (`role="status"`). Each word chip is a button opening the
  word panel; the bingo chip reads as a plain label.
- **Rack and tray** — the rack row holds the hand; the recessed tray beneath stages exchanges and
  doubles as parking space while thinking. Each row reserves exactly one tile of height, so lifting
  a tile, staging an exchange, or laying the whole hand on the board leaves every other region
  where it stands.
- **Controls** — three fixed slots: quiet Pass on the left, armed while the seat is acting, the
  primary contextual button (`Play · 34`, `Premove · 21`, `Exchange 3`) centered, and a quiet
  toggle on the right that reads Recall while pending tiles stand on the board and Shuffle when
  the rack is whole.
- **Docket** — two one-line summaries side by side: the latest move (opening the recent-move list)
  and the remaining-tile count (opening the letter tally); both panels pop above the summaries, and
  opening one closes the other.

## Word panel

A word chip answers whether the table accepts the word; the panel it opens answers what the word is. It
stands in the sheet stratum the blank picker uses — scrim beneath the sheet, both beneath the game-over
overlay — and reads at two depths.

- **Chip card** — the word, its points, its dictionary state, and one block per **reading**: the part of
  speech, the base form, and the odmiana of the form as it stands. A word with several readings stacks
  them, which is the case the panel exists for: PIŁA is a noun and a past form of *pić*. Each block
  carries a `Cała odmiana` control.
- **Odmiana sheet** — the chosen reading's whole paradigm: case × number for nouns, numerals and
  pronouns; case × gender titled by number and degree for adjectives; person × number for finite verb
  forms and gender × number for past forms, both titled by mood and tense, with the infinitive,
  participles and gerund as lists beside them; degree rows for adverbs; one list for invariant parts.
  Every grid on one sheet shares a single column axis, so several grids read as one table; a grid wider
  than the sheet scrolls sideways in its own frame; and a form the grids hold no cell for joins a titled
  list, so the sheet carries the reading whole. A cell the paradigm leaves empty prints an em dash.
  Forms the table's dictionary accepts read as playable, the rest carry a struck-through treatment, and
  the form standing on the board reads in the accent. A back control returns to the card, and a reading
  strip stands beside it whenever the word carries more than one reading.

The panel holds the word it opened for, so a move arriving from another seat leaves it standing and
honest. Escape steps the sheet back to the card, the card to closed, and reaches the lift and recall
vocabulary only after that; the primary action rests while the panel stands. A long paradigm scrolls
inside the sheet, so the board keeps its size at every depth.

Three gestures reach the panel:

- **A chip in the feedback line** opens the word the arrangement in progress forms, carrying the verdict
  the table gave it.
- **A played word in the move log** opens as a control of its own, so every word the table has accepted
  stays readable. The log is also the keyboard route into the panel, since it names the words the board
  carries.
- **A press and hold on a standing tile** opens the words running through that square. The board answers
  for what stands on it, and tiles still being arranged answer through their chips, which keeps the hold
  clear of the drag gesture. The square shows the press building for the length of the hold, so the
  gesture teaches itself, and a release before the end leaves the board as it was. The hold consumes the
  press it rides on, so the tap a touch would spawn stops at the tile instead of reaching the panel. The
  board stands at every viewport, which makes the hold the one way in that survives the compressed
  portrait layout folding the docket away.

A square where two words cross opens the card with a **word strip** — the pill toggle the odmiana sheet
uses for readings — so each word is reachable from every tile it owns. The strip stands on the card; the
sheet keeps the reading strip. The panel prints a score where the score is known, which is the chip and
the log; a standing word read from the board prints its state alone, since the bonuses under it were
spent on the turn that played it.

Grammar terms arrive as data in Polish — `rzeczownik`, `mianownik`, `pojedyncza` — and print as they
arrive. The frame around them is interface text, and the asked word prints in the canonical uppercase the
tiles carry while base forms and paradigm cells print lowercase.

## Gesture vocabulary

One pointer code path serves mouse and touch: press-and-release within 6 px is a tap, further
travel is a drag, and a press held in place on a standing tile reads the word instead of moving it. On touch, the carried tile ghosts above the finger and the computed target cell
shows a high-contrast ring. While a tile travels, its resting place dims to a shadow, and the row it
would join — rack or tray — carries an accent ring with a tile-shaped landing slot at the insertion
point. The page holds one scale: pinch zoom, double-tap zoom, and the long-press callout stay off, so
a gesture over the board is always a game gesture.

Desk effects — the only mutation vocabulary, shared by tap and drag:

| effect | meaning |
|---|---|
| `lift` | pick a tile up from rack, tray, or a pending cell |
| `lay` | put the lifted tile on an empty cell (a blank opens the letter picker) |
| `take-back` | return a pending tile to the rack |
| `park` / `retrieve` | move a tile into or out of the exchange tray |
| `reorder` | insert a tile at a new rack position (persisted via the `reorder` action) |
| `recall` | return every pending tile to the rack |
| `shuffle` | randomize the local rack order |

Tap and drag reach the same places. A tap lifts the tile it lands on — rack, tray, or a pending
board square — and the next tap sets it down: an empty square moves it, a rack tile inserts it
before that tile, a tray tile parks it there, and the "Return here" and "Park here" slots take it at
the end of a row. Tapping the lifted tile again puts it back. One tile is lifted at a time. Escape
clears the lift, then recalls; Enter fires the primary action when it is armed. The blank picker is a
sheet with the scheme's own alphabet.

## State vocabulary

- **Turn**: `acting` (me ∈ to_act) versus `watching`; acting flips the banner to accent strength,
  rings the board frame and my plaque, retitles the tab, and may vibrate. The turn-notice toggle
  adds a page notification for the moment my turn opens while the tab rests, and keeps the event
  stream connected while the page is hidden so that moment arrives.
- **Premove**: plays and exchanges queue while off turn; a pass always plays on the turn.
  `queued` (the committed tiles leave the rack and stand as board ghosts in the premove accent,
  beside a "Premove queued — Cancel" chip; submitting again replaces the queue) → `applied`
  (tiles become real with the fresh-play flash) or `returned` (tiles back on the rack with the
  reason in the feedback line).
- **Word status**: `unknown` (hollow dot) · `valid` (success accent) · `invalid` (danger, with the
  dictionary's sentence in the guidance line) · `standing` (reserved for challenge schemes).
- **Word insight**: `absent` (the dictionary refuses the word) · `unclassified` (the word plays, and the
  morphology sources carry no analysis for it) · `read` (readings arrived). Sample data carries a badge
  on the card and marks its own forms unplayable, so the single claim a sample card makes is the
  dictionary's verdict on the asked word. Each paradigm form carries `playable`, and the form on the
  board carries `standing`.
- **Exchange**: tiles in the tray arm `Exchange N`; the guidance line carries the remaining
  exchange budget and the bag minimum.
- **Connection**: `joining` · `live` · `resuming` · `lost`, shown as a quiet chip in the status
  strip.
- **Fresh play**: one frame in the mover's tint, haloed in the same tint, drawn around the latest
  play as a whole — a single rectangle from its first new letter to its last, taking in the standing
  letters the play hooked through — and it stands until the next play. While the play is still
  someone else's news, its tiles bob in place one after another along the word — three hops, a few
  seconds of quiet, again — and settle for good at the first sign the player has seen them: a press
  anywhere on the board, or any tile moved at the desk. A play of your own arrives already seen. The
  `calm` motion setting and a device asking for reduced motion keep the frame and the halo and leave
  the tiles still. The move log keeps the longer memory.

## Feedback policy

Derived from the table description, consumed as data. Action legality (line, gaps, anchoring, the
center rule) is always computed live on the client. Word verdicts follow the policy: `live` (the table
answers word checks, so each formed word carries its verdict as it stands), `submit` (the server
answers on submission), `challenge` (reserved: plays stand until contested). A table advertises the
live path through `parameters.word_check`, which holds while the scheme validates on play and its
dictionary is loaded; the interface asks `GET /tables/{id}/words` for the words it shows and
remembers every answer. The word-status vocabulary above is the seam that lets challenge schemes
arrive without redesign.

## Preferences

Four choices belong to the device rather than to a table: the color mode, the interface motion, the
language, and the turn notice. They travel together as one record that every tab on the device
shares, and the first three follow the same three-state shape — a system setting that reads what the
device already says, and an explicit choice that overrides it on the document root (`data-mode`,
`data-motion`, `lang`). Motion at `calm` stills the acting plaque's breath, the fresh-play cue, and
the tile lift; at the system setting `prefers-reduced-motion` decides. A device that made its choices
under an earlier version keeps them.

## Theming and tokens

A theme is a named token set with light and dark variants, sourced from `config/styles/<name>.yaml`,
served once per table, and mapped onto CSS custom properties. The viewer's `prefers-color-scheme`
picks the variant, with a manual override. Geometry is theme-independent: tile radius ≈ 1/7 of the
tile side, the category band ≈ 1/7 of the board-tile side, hairline grid of 1 px, rack tiles at
least 40 px wide, board cells degrade to a 20 px floor.

Token vocabulary (per variant): `chrome` (surface, panel, edge, text, muted) · `board` (surface,
grid, frame, star, premium_label_share) · `premiums.word_2/word_3/letter_2/letter_3` (fill, label) ·
`category_premiums.yellow/green/blue/red` (fill, label) · `tiles` (face, edge, text, face_tint;
band per category) · `accents` (primary, on_primary, danger, success, premove).

Each category's tile face is derived, per variant, as `mix(tiles.face, tiles.band[category],
tiles.face_tint)` — a linear per-channel sRGB blend — so tiles carry a wash of the color they hold.

The premium glyph is derived by the same blend: `mix(premium.fill, premium.label,
board.premium_label_share)`. The authored `label` stays the ink that belongs on each fill, and one
number per variant says how much of it to print, so the board holds its multipliers as a watermark
readable on inspection and unobtrusive at a glance. Both games and every layout follow the one
number. The center square is the exception the watermark makes: it keeps its premium fill and prints
the star in `board.star` at full strength, because where the first word must cross is information the
player needs at a glance.

Every consumer of the tokens (the CSS custom properties, the asset generator) derives faces and
glyphs with the same formulas.

### Player tints

Eight hues, chosen apart from the four category hues, shared across themes. Hue says who; strength
says whose turn.

| tint | value |
|---|---|
| carmine | `#AF4A54` |
| coral | `#D07A4F` |
| copper | `#A8703D` |
| teal | `#2FA08C` |
| azure | `#3FA3CF` |
| indigo | `#5668C9` |
| violet | `#8A5BB8` |
| graphite | `#6E7B8A` |

### Lniany — the default theme

| token | light | dark |
|---|---|---|
| chrome.surface | `#F3EDDF` | `#211B13` |
| chrome.panel | `#E9E1CD` | `#2E271C` |
| chrome.edge | `#D8CDB2` | `#3E3526` |
| chrome.text | `#2B2419` | `#EDE4D0` |
| chrome.muted | `#7A6C55` | `#9A8D74` |
| board.surface | `#EDE5D1` | `#322A1E` |
| board.grid | `#D9CEB6` | `#453B2B` |
| board.frame | `#7A5F44` | `#4A3A29` |
| board.star | `#8F3A24` | `#E8967E` |
| board.premium_label_share | `0.20` | `0.20` |
| premiums.word_2 | `#D8CBA8` / `#6C5B39` | `#4A4030` / `#C8B98F` |
| premiums.word_3 | `#7B6142` / `#F3EBDA` | `#6B5334` / `#EFE3C8` |
| premiums.letter_2 | `#C4D5DE` / `#38607A` | `#24394A` / `#8FC0DE` |
| premiums.letter_3 | `#8FB3C4` / `#1F455C` | `#2F4A5E` / `#BFDCEE` |
| category_premiums.yellow | `#EBD188` / `#8A6A14` | `#4E3E10` / `#E5C05C` |
| category_premiums.green | `#C9D4A6` / `#4E6626` | `#364219` / `#B7CC7E` |
| category_premiums.blue | `#BACFDD` / `#2F5A78` | `#22394A` / `#8FC0DE` |
| category_premiums.red | `#E3B8A8` / `#8F3A24` | `#4C2417` / `#E8967E` |
| tiles.face | `#FAF3E1` | `#F2E7CB` |
| tiles.edge | `#CFC3A4` | `#B7A784` |
| tiles.text | `#241E14` | `#241C10` |
| tiles.face_tint | `0.25` | `0.25` |
| tiles.band.yellow | `#D9A226` | `#E0AB2B` |
| tiles.band.green | `#67903F` | `#7BA34C` |
| tiles.band.blue | `#38719B` | `#4E86B4` |
| tiles.band.red | `#AC4029` | `#C04E33` |
| accents.primary | `#7C3F4E` | `#B36A79` |
| accents.on_primary | `#FCF7EC` | `#2A161B` |
| accents.danger | `#9A2F1F` | `#D96A50` |
| accents.success | `#3F7A4B` | `#7FBF8C` |
| accents.premove | `#6D5E8E` | `#8E7FB5` |

Premium cells carry a fill and a glyph washed toward it; tiles keep a light face in both variants — physical
tiles under lamplight — with the category as an enamel band along the bottom edge and a
`face_tint` wash of the band color across the face. A blank belongs to no category, so its band is
derived as the midpoint of `tiles.edge` and `chrome.muted` and washes the face through the same
`face_tint` formula: a neutral tile that keeps the relief every other tile has. Blanks show a hollow
diamond and print their assigned letter once played. The letter-multiplier rows serve the
Scrabble board and are provisional until its specimen renders in the asset phase.

## Type

The product face is Lato (SIL OFL, by Łukasz Dziedzic): Black for tile letters, headings, and the
primary button; Semibold for labels and names; Regular for running text. Digits in scores, clocks,
and logs use tabular figures.
