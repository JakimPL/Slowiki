## General workflow

* While executing plans, stop after each phase, unless told otherwise.
* After ending each phase, write one sentence at the end about the next phase or the plan finalization. Propose a brief commit message of the following form: _Did: what_, e.g. _Refactored: musical arrangement dataclass_.
* While developing, look for `guidelines.md` in the working repository. Read this before coding.

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
* State functionality in positive terms. Describe what a class or function *does* — not what it avoids, omits, skips, differs from, or no longer does. Reframe every negation ("does not", "rather than", "instead of", "without", "never", "cannot", "no longer") into the behaviour that actually happens. Do not contrast with rejected alternatives as justification; the positive statement carries the meaning. Negative phrasing is allowed only where the condition itself is the contract: exception triggers in `Raises:` clauses, precondition/postcondition bounds (prefer "must be at least X" over "cannot be less than X" where natural), and documented edge-case returns. Outside these concrete cases, negative descriptions are information noise and must be removed.
* Avoid code comments. Comments are acceptable for tensor shapes, third-party API quirks, or non-obvious invariants.
* Avoid comments and docstrings that restate code.
* Don't write module docstrings and constant descriptions.
