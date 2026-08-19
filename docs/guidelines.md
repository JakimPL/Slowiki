## General workflow

* While executing plans, stop after each phase, unless told otherwise.
* After ending each phase, write one sentence at the end about the next phase or the plan finalization. Propose a brief commit message of the following form: _Did: what_, e.g. _Refactored: musical arrangement dataclass_.
* While developing, look for `guidelines.md` in the working repository. Read this before coding.
* Frontend work follows `docs/frontend.md`; interface changes start by amending `docs/interface.md`.
* Dictionary and lexicon work follows `docs/lexicon-contract.md`; read the contract before touching `lexica` or `wordtable`, and start a new artifact kind as a row in its table.

## Git

* Don't commit changes, unless asked directly to do so.
* Avoid using `git stash`. Ask for permission if you need it.
* Use `gh` only for read-only operations. Ask for permission if a `gh` operation writes anything.
* NEVER mention AI/Claude/Claude Code authorship in commit messages (no Co-Authored-By, no “generated with” footers).

## Development

### General

* Keep code modularized around clear ownership boundaries.
* If a function has several meaningful steps, split them into helpers with one clear responsibility.
* Prefer subpackages over large modules or flatten directory structure.
* Run `pre-commit` on a new portion of code after each phase.
* Do not abbreviate variable names. Use `note`, not `n`.
* Restrict yourself from using default values for non-optional, excluding these that are not meant to be frequently changed (e.g. seed). If you do use defaults, declare a Final top-level constant for that.
* Be explicit about type expectations. Avoid dynamic `getattr` or `hasattr`.

### Function shape

* Functions read as prose: an orchestrator names its steps at one level of abstraction and delegates each step to a helper named for its intent. If a reader must decode indices, coordinates, or state mutations inline — roughly anything past 15 lines of low-level work — the function does too much and must be split.
* Each validation rule is its own `_ensure_*` helper that raises the domain error; the orchestrator reads as the list of rules it enforces.
* Symmetric variants (horizontal/vertical, open/close, increment/decrement) are one function with a parameter, never two mirrored copies. Duplication that differs only by a transposition is a defect.
* Helpers return values. A helper that mutates its argument and returns `None` hides the data flow and invites the caller to forget the result; build and return the new value instead.
* Every game-rule number that a scheme could reasonably tune lives in the scheme configuration and flows through a parameters model. A `Final` module constant is reserved for genuinely fixed protocol values (formats, wire markers, retry buffers).

### Modules

* One concept per module. A model or enum shared across packages gets its own module named after the concept; splitting later is a rename, never an untangling.
* Import every name from its defining module. Implicit re-exports (importing `X` from a module that itself imported `X`) are forbidden — they hide the owner and break when the intermediary changes.

### Boundaries

* External text — CLI arguments, configuration files, request payloads — is parsed once, at the boundary, into a typed structure (`NamedTuple` or Pydantic model) with explicit arity and value checks. Positional indexing of raw input is allowed only inside that parser.
* Normalization happens once, at ingestion. Letters are canonically uppercase across the whole system (dictionary loaders, tile presets, blank assignments); join codes are canonically uppercase. Code past the boundary compares values directly and never calls `upper()`/`lower()` again.
* Program status output goes through `logging`, configured at the entry point. `print` is reserved for data explicitly requested by the user (e.g. a value the CLI was asked to produce).
* Compiled dictionary artifacts obey `docs/lexicon-contract.md`: `lexica` owns the bytes, the kinds, the formats and the readers, `wordtable` owns the paths, the builds, the caching and the dispatch, and the engine sees one verdict port. An artifact kind exists once it holds a row in that document's table, and `make contract` — also a pre-commit hook — holds the document and the code in agreement.

### Typing

* Specify all input and return types in function signatures, including `None`.
* Fill generic types. Use `dict[str, int]`, not a bare `dict`. Avoid `Any` and `object` unless the boundary genuinely accepts arbitrary data.
* Do not cast/silence type errors unless the boundary is an untyped or mistyped third-party API.
* Validate with `mypy`.

## Error Handling

* Let failures crash unless the code can recover meaningfully.
* Bare `except` and `except Exception` are forbidden.
* Handle errors at the execution boundary when possible.
* Error handling blocks should cover only the code that is subject to a failure, unless there is a valid reason.

## Models

* Prefer Pydantic models for validated or serialized data, unless the overhead is a real risk.
* Use `frozen` when instances are not meant to change.

## Documentation

**Warning:** At this stage of the development we **don't** write neither docstrings or code comments. These rules will apply later on.

* Documentation should explain the intention of a class/function and context of usage.
* Be concise and stay factual. Avoid dwelling into technical nuances unless such discussion is necessary.
* State functionality in positive terms. Describe what a class or function *does* — not what it avoids, omits, skips, differs from, or no longer does. Reframe every negation ("does not", "rather than", "instead of", "without", "never", "cannot", "no longer") into the behavior that actually happens. Do not contrast with rejected alternatives as justification; the positive statement carries the meaning. Negative phrasing is allowed only where the condition itself is the contract: exception triggers in `Raises:` clauses, precondition/postcondition bounds (prefer "must be at least X" over "cannot be less than X" where natural), and documented edge-case returns. Outside these concrete cases, negative descriptions are information noise and must be removed.
* Avoid code comments. Comments are acceptable for tensor shapes, third-party API quirks, or non-obvious invariants.
* Avoid comments and docstrings that restate code.
* Don't write module docstrings and constant descriptions.
