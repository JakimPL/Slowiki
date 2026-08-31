# Frontend

The code contract for the player interface. `docs/interface.md` fixes what the interface *is* —
regions, gestures, states, tokens — and this document fixes how its code is organized, so the
frontend grows without inconsistency, duplicate solutions, or tangled information flow. A change that
contradicts a principle here starts by amending it.

## Principles

F1. **Two strata: reasoning and presentation.** One stratum reasons about the game on the client —
    deriving state, geometry, previews, session and device concerns — as plain functions over plain
    data, plus the hooks that hold them. The other presents: components read those values and emit
    intents. A component computes nothing a function could compute. Where presentation must measure
    the document, it takes the measurement and hands it to a function that owns the arithmetic. This
    split is what lets the whole suite run without a browser.

F2. **One concept per module, named after the concept.** A type shared across modules gets its own
    module named after it, so splitting later is a rename rather than an untangling. Every name is
    imported from the module that defines it; re-exporting through an intermediary hides the owner.

F3. **The wire stops at the boundary.** One layer knows request shapes, response shapes, and status
    codes, and its types are generated from the server's own document rather than written by hand.
    Past that layer the app speaks its own vocabulary, so a wire change lands in one place.

F4. **Server data is data, never branching.** Rule parameters, the alphabet, the feedback policy, the
    admission shape — each arrives as a value and the interface renders from it. A game or scheme
    named inside a conditional is a defect: it means the interface learned something the table was
    supposed to tell it.

F5. **One source of truth per fact.** Position and company come from the live stream; the desk in
    progress is local; neither copies the other. Effects synchronize the world outside the app —
    document title, storage, notifications, the address — and never carry the app's own data from one
    holder to another.

F6. **Every word comes from the catalog.** No user-facing text is written in a component. Keys are
    generated from the source catalogs, so a missing or misspelled key fails compilation, and counted
    phrases go through the plural machinery rather than through string concatenation.

F7. **Color and metric come from tokens.** The theme arrives as tokens and becomes custom properties;
    components set properties and the stylesheet spends them. A derived value — a tint, a wash, a
    watermark — is derived once, from a named share, by every consumer that needs it, using the same
    formula. No color literal lives in a component, and no layout number is written twice.

F8. **One stylesheet, one vocabulary.** Class names name regions and roles; state rides on data
    attributes, so an element reads its own state and a selector never encodes a parent's logic.
    Breakpoints reshuffle grid areas and reserve space; they leave a region's own styling alone. A
    preference with a system default follows one three-state shape: the system value in the base
    rules, the system-detected variant behind a media query guarded against an explicit choice, and
    the explicit choice on a root attribute.

F9. **One pointer path.** Every pointing device — mouse, pen, touch — goes through the same
    press-travel-release session, and tap and drag are outcomes of that one session rather than two
    implementations. A gesture that needs a second pointer declares itself the moment that pointer
    arrives and takes the session over cleanly, so the two never both act on one touch.

F10. **Preferences are a layer.** Choices a player makes about the app rather than about a game live
     in one typed record with one owner, one set of defaults, and one surface that changes them.
     Storage scope is a deliberate decision: a per-device preference persists across tabs, a per-tab
     fact stays in its tab. Reading a preference works before the app renders as well as during it,
     and one provider at the root carries the record to whatever reads it — a route reserved for
     device facts, never for the state of a game.

     A remembered choice about a *game* — a named rules record the player keeps for next time — is a
     second layer with its own owner, its own key and its own parse tolerance: it is game data, so it
     stays out of the device record and out of the provider that carries it. Both layers keep one
     storage shape: a pure module owns the key, takes `Pick<Storage, …>` so a test supplies its own,
     and reads defensively enough that a document written by another version still yields what it can.
     A saved record states its deviations from the game it came from, and the live catalog is what
     resolves them, so a setting added since it was saved arrives at the server's own default.

     One layer holds the whole settings vocabulary. `play/rules/` reasons about the rules a table
     plays by — the record, the changes laid over it, the catalog as a discriminated union of
     controls, the letters a preset pair expands to, the saved records and their storage, and the one
     list presenting built-in schemes and saved records alike — and `table/rules/` presents them.
     Nothing outside that layer decides what a setting means.

F11. **Failures are states.** A refusal becomes a typed value at the boundary, carrying its code and
     its sentence, and renders into a slot that reserves its space. The interface distinguishes what
     the player must decide from what the app can settle by itself.

F12. **Recover before reporting.** A client that finds itself behind re-reads the position and
     completes what the player asked for. It reports when the answer needs a person: a move the
     position genuinely refuses, a connection that stays down, a table that no longer exists. A
     retry that could apply an action twice is bounded by evidence the server rejected the first
     attempt.

F13. **The stream states its own liveness.** A quiet table and a dead connection look alike, so the
     stream carries a heartbeat, and the client treats silence past that beat as a dropped connection
     and reconnects. Every path back into view — a reconnection, a page returning from hidden —
     re-reads the position rather than assuming it kept up.

F14. **Tests reach the logic.** Pure modules carry the behavior tests, which is why they hold the
     behavior. Components are checked as rendered markup: what the player is offered, and what stays
     out of reach. Behavior that only a real browser event can reach belongs in a pure module with a
     binding thin enough to read.

F15. **Every control is a real control.** Actions are buttons, groups are labeled, labels come from
     the catalog, pressed and open states are announced, and focus stays visible. An affordance
     reachable only by a gesture gets a second route that a keyboard can take.

## Where a new concern goes

1. **Is it reasoning or presentation?** Anything that answers a question about the game or the
   session — what is legal, what it scores, what state we are in, what to store — is reasoning and
   belongs in a pure module, with a hook only if it must hold state across renders. Anything that
   answers *how it looks* is presentation.
2. **Name the concept, then place it.** The module is named after the concept and joins the
   subdirectory that owns that concern; a concept without a home means a missing subdirectory, not a
   bigger module.
3. **Does it need a value from the server?** Then the boundary layer learns the shape, the generated
   types are refreshed, and everything past the boundary consumes the value as data (F3, F4).
4. **Does it show words?** They go into the source catalogs and reach the code as generated keys (F6).
5. **Does it show color or spacing?** It becomes a token or spends one; a new derived value declares
   the share it derives from (F7).
6. **Does it remember something?** Decide the scope first — device or tab — then name the layer it
   belongs to: device preferences, or the saved rules a player keeps for a game. Each layer owns one
   key, so a fact joins the layer that owns its kind (F10).
7. **Does it take a gesture?** It joins the existing pointer session rather than listening on its own,
   and its arithmetic is a function that takes points and rectangles (F1, F9).
8. **Write the test where the behavior is.** A rule gets a unit test; a rendered offering gets a
   markup test; both, when a rule decides what is offered (F14).
