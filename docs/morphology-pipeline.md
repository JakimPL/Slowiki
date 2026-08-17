# Morphology pipeline

This document records the design of the Polish morphology pipeline in
`lexica`: classification into części mowy, recognition of all inflectional
variants, equivalence classes with homonym robustness, a compiled game
artifact, incremental re-runs, and correction handling. Grammar terminology
and the source survey live in `docs/morphology.md`.

## Goal

For every word in the game dictionary the pipeline produces:

1. a classification: część mowy plus grammatical tags for the form,
2. equivalence classes: a lemma with its part of speech and inflection
   pattern grouped with all its inflected variants,
3. homonym robustness: one surface form maps to several classes where its
   paradigms overlap,
4. a base relationship: every class exposes a base selected by the active
   rules, with canonical defaults.

The unit is the class (paradigm), not the lemma alone and not the stem:
variants are grammatical forms, recognised from source data that lists every
form of every paradigm.

## Current state of the repository (verified)

- `lexica` compiles `dictionaries/sjp-20260803.zip` (slowa.txt: 3,240,429
  lowercase forms, CRLF, UTF-8) into `dictionaries/sjp-20260803.v1.lexicon`.
- The artifact is a `marshal` dump of a tuple of uppercased, sorted,
  deduplicated words; no header; versioning lives in the filename via
  `LEXICON_FORMAT: Final = 1` in `src/wordtable/paths.py`.
- `src/wordcore/lexicon/protocol.py` declares the `Lexicon` protocol:
  `judge(word) -> WordVerdict` and `has_prefix(prefix) -> bool`.
  `src/wordcore/lexicon/lexicon.py` implements `TextLexicon` with bisect
  lookups.
- Play validity runs through `src/wordcore/rules/validity.py`
  (`invalid_words`, `validate_words`), called from
  `src/wordgames/backend/base.py` under `GameParameters.validate_on_play`
  (`src/wordgames/backend/parameters.py`).
- `src/lexica/models.py` holds a dormant `WordEntry` (surface, base_form,
  homonym_id, categories, variants, status, source) awaiting exactly this
  feature; the `lexica label` CLI subcommand is a stub.
- Import-linter contracts: `wordcore` imports nothing from `lexica`; the game,
  dictionary, and bot layers stay independent. Morphology therefore reaches
  the engine through the `Lexicon` protocol.
- `src/wordtable/lexicons.py` loads one `Lexicon` per `DictionaryName`
  (`sjp`, `english`, `osps`) through `LexiconService`, cached, with loads on
  `asyncio.to_thread`.
- The per-observer projection (`src/wordcore/views/projection.py`,
  `PositionView`) carries `last_play: PlayRecord | None`, and
  `src/wordserver/describe.py` builds the table description
  (`RuleParameters` in `src/wordserver/models/rule_parameters.py`).

## Phase 0 measurements (2026-08-17)

Verified facts from the source-and-license gate:

- morfeusz2 `pl.sgjp.sgjp-2026.06.01` classifies 83.22% of słowa.txt and
  separates paradigm-level homonyms via pattern-qualified lemmas
  (`zamek:Sm3~a` / `zamek:Sm3~u`); `generate()` enumerates full paradigms.
- PoliMorf 0.6.7 (tabular, BSD-2-Clause) rescues 36.85% of the SGJP-unknown
  forms; combined coverage 89.40%, remaining 10.60% → UNKNOWN report.
- 37.66% of forms carry multiple interpretations (max 48); the measured
  class-key count is 361,664.
- Full analysis pass ≈110 s; case-insensitive results.
- Specimen corpus: `dictionaries/specimens/specimens.yaml` (4,156 words,
  seed 20260817, 671 UNKNOWN specimens, reference analyses included) lives in
  the gitignored `dictionaries/` tree; the 159-word stress anchor commits as
  `tests/specimens/stress.yaml`.

## Pipeline stages

1. **Ingest** — reuse `iter_sjp_words` (`src/lexica/dictionaries/sjp.py`):
   decode, strip, uppercase. Uppercase canonicalization stays here (P7).
2. **Analyse** — look up each form in morfeusz2 (bundled SGJP 2026.06.01);
   forms tagged `ign` fall back to the PoliMorf 0.6.7 tabular data with a
   `source` flag. Each hit yields lemma + tags + pattern/qualifier. One
   module per source under `lexica/morph/sources/`, mirroring the
   `lexica/dictionaries/` layout.
3. **Classify** — map source tags to `PartOfSpeech` and grammatical tag
   enums through the deterministic mapping table (`docs/morphology.md`).
4. **Assemble** — group analyses by (lemma, part of speech, pattern,
   qualifier) into classes; enumerate every paradigm variant with tags; flag
   each variant `in_dictionary`; compute the canonical base per POS.
5. **Report** — emit `UNKNOWN` entries, per-POS coverage, homonym
   multiplicity, all visible in a committed report.
6. **Compile** — serialize the artifact v2.
7. **Consume** — rules filters during play validation and class info in the
   UI.
8. **Maintain** — input digests, diffs, overrides.

## Data model (Phase 1 formalizes)

Frozen Pydantic models in a new `lexica/morph/` subpackage (one concept per
module):

- `PartOfSpeech` — StrEnum with the ten Polish names plus `INNY`.
- Tag enums — `Przypadek`, `Liczba`, `Rodzaj` (m1/m2/m3/f/n), `Osoba`,
  `Czas`, `Tryb`, `Aspekt`, `Stopien`, `CzasownikForm`, `LiczebnikTyp`,
  `ZaimekTyp`.
- `Analysis` — lemma, part of speech, tags, pattern, homonym qualifier,
  source (`sgjp` / `polimorf`).
- `VariantRecord` — form, tags, `in_dictionary` flag.
- `ClassRecord` — stable `class_id` derived from (lemma, POS, pattern,
  qualifier); the SGJP pattern-qualified lemma (`kot:Sm1`) supplies the
  pattern directly. Fields: part of speech, base, tuple of variants.
- Entry model — the dictionary surface maps to a tuple of class ids; the
  existing `WordEntry` becomes the surface-level record, enriched with
  status `CLASSIFIED` / `UNKNOWN`.

The class stores the full paradigm, so any base projection remains possible;
base selection is a pure function of (class, rules) with canonical defaults
(noun: mianownik lp; verb: bezokolicznik; adjective: mianownik lp rodzaj
męski; uninflected: the form itself).

## Artifact v2

- `lexica/compile.py` writes a marshal envelope: format header, sorted
  surface→class-ids index, classes table, alphabet. The loader validates the
  strict shape and rejects malformed files.
- `LEXICON_FORMAT` becomes 2; the filename version retires v1 artifacts.
- `wordcore/lexicon/morph.py` implements `MorphLexicon`: `judge` and
  `has_prefix` via bisect with results identical to `TextLexicon`, plus
  `analyses(word)`, `classes_of(word)`, `variants(class_id)`,
  `base_of(class_id, rules)`.
- `wordtable/lexicons.py` loads `MorphLexicon` for `sjp` and keeps
  `TextLexicon` for `english` and `osps` (per-dictionary lexicon kind).
- Memory estimate: 3.24M surfaces plus ≈362k measured class keys with
  variants, roughly 150–250 MB at startup; measured in Phase 3 with
  mitigation options (slimmed tags, lazy class table).

## Determinism and stability

The shipped pipeline is fully deterministic: analysis is dictionary lookup,
classification is a pure table, assembly is grouping. A rerun over the same
inputs produces byte-identical artifacts.

Corrections follow three visible channels:

- an overrides YAML (`dictionaries/sjp-20260803.morph.yaml`, gitignored) forces
  analyses for specific forms — additions and removals — and fails loudly when
  a target form is absent from the dictionary or a marker appears twice; an
  empty `analyses` list forces the form to UNKNOWN and skips PoliMorf rescue,
- the `UNKNOWN` report lists every uncovered form instead of guessing,
- `lexica diff <old> <new>` shows added, removed, and changed surfaces and
  classes between artifact versions; `lexica report <artifact>` prints the
  artifact statistics.

An optional review tool may later assist with the `UNKNOWN` report; its
proposals land in the overrides file after approval. The shipped path remains
independent of any model.

## Incremental processing

- The compile step records input digests in a manifest
  (`dictionaries/sjp-20260803.manifest.json`, gitignored): sha256 over the
  archive bytes, the PoliMorf source, the overrides file, the analyzer
  dictionary identity, and the mapping table version. A compile with
  unchanged digests and an existing artifact skips; edits to the overrides
  file or a dictionary upgrade invalidate the artifact.
- The analysis pass is cheap (in-memory lookups), so the full pass recomputes
  on change; `lexica diff` exposes exactly what changed and a rerun over the
  same inputs produces byte-identical artifacts.
- Words removed from the dictionary leave the surface index automatically;
  classes rebuilt from current forms drop members that vanish, and classes
  with zero remaining dictionary members are pruned. Grammar completeness of
  variants stays independent of dictionary membership through the
  `in_dictionary` flag.

## Game integration

- The `Lexicon` protocol (`src/wordcore/lexicon/protocol.py`) gains the
  morphology queries; `TextLexicon` and `MorphLexicon` both satisfy it.
- `GameParameters` gains `allowed_pos: tuple[PartOfSpeech, ...] | None` and
  `base_form_only: bool` (both default to the current behaviour);
  `SchemeConfig`, `config/schemes/*.yaml`, `wordtable/build.py`, and
  `wordserver/describe.py` thread them through. `validate_words` rejects
  words whose analyses violate the filters with a precise verdict; `UNKNOWN`
  words pass dictionary validity and are rejected under active filters.
- UI info: the table view enriches the last play or a read endpoint exposes
  class info for placed words; `scripts/openapi.py` regenerates the
  frontend types.

## Development corpus

`tests/specimens/stress.yaml` commits the hand-reviewable golden anchor: the
homonym stress list from `docs/morphology.md` (159 words) with its reference
analyses from `pl.sgjp.sgjp-2026.06.01`. The full stratified corpus
(4,156 words: a 60k-word uniform pool drawn with seed 20260817, proportional
per-POS quotas, min 2 per observed tag prefix, 671 UNKNOWN specimens by
design) lives in the gitignored `dictionaries/specimens/specimens.yaml` for
broad regression runs.

Both files regenerate deterministically from the SJP archive and the pinned
analyzer:

```
uv sync --extra morphology
uv run python scripts/specimens.py
```

The script (`scripts/specimens.py`) draws the same seed, the same pool, and
the same stress list, so regeneration reproduces both files byte for byte.

## Patterns reused from the ContextGraph project

The sibling repository `/home/jakim/Projects/Python/ContextGraph` runs an
LLM-assisted pipeline and contributes patterns for the optional review tool
(verified by reading its source):

- `LLMClient` protocol with `Prompt(system, instruction)` and
  `complete_structured(prompt, response_model)`; clients per backend
  (Anthropic, Ollama, DeepSeek) with structured-output enforcement.
- Content-addressed response cache: sha256 over (descriptor, prompt, JSON
  schema), sharded JSON files, so prompt or schema edits silently earn fresh
  answers and a stage resumes for free.
- Transient-error retries with exponential backoff; 429/5xx mapped to
  retriable.
- Versioned markdown prompt templates shipped in-package.
- `pipeline.json` manifest with per-stage input sha256 for skip-when-unchanged
  logic.
- Overrides YAML with fail-loud exact-once validation, hashed into the stage
  digest.
- `ScriptedClient` fake plus `monkeypatch build_client` for LLM-free tests;
  golden end-to-end runs through the real CLI.

## Testing matrix

| Concern | Test |
|---|---|
| Tagset mapping | golden tag examples per POS, e.g. `subst:sg:inst:f` → RZECZOWNIK, narzędnik, lp, f |
| Homonyms | stress list: bronią → 2 classes; zamek → 2 classes with distinct dopełniacz |
| Specimens | stress anchor passes golden expectations; full corpus (gitignored) optional regression |
| Artifact | round trip, strict-shape rejection, `LEXICON_FORMAT` retirement |
| Parity | `judge`/`has_prefix` of `MorphLexicon` equal `TextLexicon` on samples |
| Filters | allowed-pos/base-form combos, `UNKNOWN` under filters, defaults unchanged |
| Determinism | two compiles byte-identical; diff empty |
| Incremental | word addition adds entries only; removal prunes classes |
| Overrides | forced analysis wins; stale target fails loudly |
| Full corpus | completes, zero crashes, every surface keeps an entry |

## Phase roadmap

0. Source and license gate (completed 2026-08-17): licenses and formats
   verified, downloads in gitignored `dictionaries/sources/`, coverage
   measured, sources decided, specimen corpus generated (gitignored full
   corpus, committed stress anchor).
1. Domain model and tagset mapping (pure models and table, unit-tested).
2. Analyzer index and class assembly with the `UNKNOWN` report; full-corpus
   run (completed 2026-08-17: 201,821 classes, 9 min 7 s, 21.8 GB peak).
3. Artifact v2 and `MorphLexicon`; parity and round-trip tests (completed
   2026-08-17: versioned marshal envelope, interned raw tuples, aligned
   surface→classes index, referential loader validation).
4. Play-validation filters through schemes and `validate_words` (completed
   2026-08-17: `allowed_pos` and `base_form_only`, config-validated, exposed
   in the table description).
5. UI class info (server surface and frontend annotation; completed
   2026-08-17: `GET /tables/{id}/word/{word}` plus tappable word chips in the
   move log).
6. Incremental operations: digests, `lexica analyze/compile/report/diff`,
   overrides (completed 2026-08-17: manifest skip, fail-loud overrides,
   byte-identical reruns); the optional DeepSeek review tool for `UNKNOWN`
   follows as a separate change.

## Risks and open questions

- The 10.60% UNKNOWN remainder lands in the report; batch review or an
  optional DeepSeek review tool may later reduce it.
- `frag`, `comp`, `adjp`, `adjc` semantics need a precise subtype decision in
  Phase 1 (they fall into LICZEBNIK / PRZYSŁÓWEK / PRZYMIOTNIK at the POS
  level).
- PoliMorf-rescued analyses merge paradigm-level homonyms (lemma-level data);
  the `source` flag records the lower fidelity.
- The pinned `morfeusz2==1.99.15` wheel fixes the dictionary data version; a
  dictionary upgrade changes the reference analyses and re-runs specimen
  regeneration deliberately.
- Memory footprint of `MorphLexicon` at server startup: the interned raw
  artifact loads in 7.7 s at 1.5 GiB resident and compiles in 3 min 51 s at
  3.4 GB peak (down from the 21.8 GB pydantic prototype). Mitigation options
  remain (slimmed tags, lazy class table).
- WSJP API access remains to confirm; paradigm-level scope holds for now.
