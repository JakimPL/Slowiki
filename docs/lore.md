# Lore

Lore is what the game answers about a word once the dictionary has accepted it:
its readings, and for each reading the lexeme it belongs to, its part of speech,
its base form and its whole paradigm. A word carries several readings where
Polish gives it several — PIŁA is a noun and a past form of *pić* — and each
reading stands on its own.

The answer is computed when it is asked for. `docs/morphology.md` holds the
grammar the readings speak in and the survey of sources that could supply them;
this document holds what the running system does with them.

## The endpoint

`GET /tables/{table_id}/lore?words=…` answers a `WordLore` per word, bounded to
sixteen words the way the verdict route beside it is:

| Field | Meaning |
| --- | --- |
| `word` | the surface as asked, canonically uppercase |
| `playable` | the table's dictionary accepts it |
| `readings` | one entry per lexeme the sources hold for the surface |

Each reading carries the lexeme token, the part of speech, the base form, and
the forms of the paradigm; each form carries its text, its `Inflection`, and
whether the table's dictionary accepts it. The panel strikes through the forms
it refuses and prints the standing form in the accent, so a sheet states the
whole paradigm and the dictionary's share of it at once.

A table offers lore when three things hold: `morfeusz2` is installed, the
dictionary carries Polish morphology (`sjp`, `osps`), and its word list is on
disk. `RuleParameters.lore` states the answer in the table description, so a
client asks only where an answer exists, and the route answers 422
`lore_unavailable` to anyone who asks anyway.

`wordtable.lore.LoreService` owns the analyser: one Morfeusz engine per
process, one rescue table per dictionary, both built on first use behind a lock
and reused for the life of the server, with the reading itself run on
`asyncio.to_thread`. The server warms the default dictionary at startup.

Lore is a pure function of the word and the dictionary. Moving it behind a
network boundary later is a transport change.

## Cost

Answering on demand is what keeps a large generated file out of the deployment.
Measured over 3,000 words drawn from the SJP list (seed 20260823), with the word
list, the analyser and the rescue table all resident:

| Metric | Value |
| --- | --- |
| One word, analysed and its paradigms generated | 3.5 ms median · 9.1 ms p95 · 21.6 ms max |
| A full sixteen-word request | ≈56 ms median |
| Forms generated per word | 62.8 |
| Peak resident: word list | 396 MB |
| Peak resident: word list, analyser and rescue table | 516 MB |

The word list dominates the memory, and the game holds it to judge words at
all; lore adds the rescue table's ≈120 MB on top of it, with the analyser's own
data mapped beneath that peak. Compiling every paradigm into an artifact was
measured at 216 MB on disk and 1.5 GB resident, so the on-demand answer is the
one that ships.

## The sources

**SGJP through Morfeusz 2** is the primary source. `build_morfeusz_engine`
builds `Morfeusz(praet="composite")` and asserts the bundled dictionary against
the pinned `SGJP_DICTIONARY`, so a wheel carrying other data stops the build.
Composite mode composes the past tense, which is what lets `biegłem` read as
`praet:sg:m1.m2.m3:pri:imperf` with its person and `zrobiłbym` as a
conditional.

`head_interpretations` decides which of Morfeusz's interpretations count as a
reading of the whole word. Morfeusz segments what it cannot read whole, so
`biegłem` also arrives as `biegł` plus `em`. The rule keeps the interpretations
spanning the whole surface, and where none does, the ones starting at its first
letter. `czyżby` therefore reads whole rather than as `czyż` + `by`, and
`biegłem` reads as *biec* alone.

`generate_paradigm` asks Morfeusz for the forms of a lexeme, keyed by the
pattern-qualified lemma, which is what fills the odmiana sheet.

**PoliMorf rescues what SGJP leaves unread.** The table is too large to consult
per request, so `wordtable rescue` precompiles the PoliMorf readings of exactly
the surfaces Morfeusz cannot read into the `rescue` artifact — 205,151 surfaces,
19.5 MB — and the service holds it in memory. `docs/lexicon-contract.md` holds
the artifact's kind and format.

The two sources answer at different fidelities, and every reading states which
answered. Morfeusz generates from a lexeme it holds while PoliMorf merges
paradigm-level homonyms under one lemma, so a rescued surface earns a part of
speech and an inflection while its paradigm stays with the forms the sources
hold. The panel shows the difference.

## Lexeme identity

`LexemeId` is the part of speech, the lemma, and SGJP's inflection pattern.
`lexeme_id_from_lemma` splits SGJP's pattern-qualified name at ingestion, so
`kot:Sm1` reaches the panel as the lemma KOT while `Sm1` stays the internal key.
The pattern is what separates paradigm-level homonyms: `zamek:Sm3~a` takes the
dopełniacz *zamka* and `zamek:Sm3~u` takes *zamku*, so the two reach the panel
as two readings with two paradigms. Sense homonyms whose paradigms coincide
share one lexeme by construction.

`select_base` picks the form the reading is named by: mianownik liczby
pojedynczej for nouns, numerals and pronouns; the same in a masculine gender and
the stopień równy for adjectives; the bezokolicznik for verbs; the form itself
for the uninflected parts. Where several forms fit the cell — variant citation
forms such as *przepaść* beside *przepadnąć* — the lexeme's own lemma wins.

## Coverage

Measured over the whole SJP list (`sjp-20260820`, 3,240,471 forms) against
`pl.sgjp.sgjp-2026.06.01` and `polimorf-20260726`. `wordtable coverage`
reproduces the table and writes it to `{stem}.coverage.json` beside
`{stem}.unread.txt`, which names every form neither source reads.

| Outcome | Forms | Share |
| --- | --- | --- |
| Read by SGJP | 2,696,562 | 83.22% |
| Rescued by PoliMorf | 205,151 | 6.33% |
| Residual | 338,758 | 10.45% |

199,843 lexemes carry the readings: rzeczownik 86,424 · przymiotnik 64,097 ·
czasownik 24,734 · przysłówek 23,571 · wykrzyknik 383 · liczebnik 206 ·
partykuła 182 · przyimek 106 · spójnik 106 · zaimek 6 · inny 28.

123,729 forms (3.82%) read into several lexemes at once — the case the panel
stacks its reading blocks for. Seven is the most any form reaches, and BOLKI
reaches it.

## The residual answers `nieznane`

A word the sources cannot read plays exactly as the dictionary allows, and the
panel says the sources hold nothing for it — `unclassified` in the interface
vocabulary (`docs/interface.md`). `{stem}.unread.txt` names the residual form
by form, so what is uncovered stays countable.

The residual is overwhelmingly regular: `nie-` on participles and adjectives,
the emphatic clitics `-że` and `-ż`, and productive derivation
(`niedociosaną`, `sztorcujże`, `putinizujesz`). Two deterministic attacks on it
were measured and left unbuilt:

| Attack | Recovers |
| --- | --- |
| Strip `-że`/`-ż` and `nie-`, re-analyse | 19.0% of the residual, 2.38% of the corpus |
| Fit SGJP inflection skeletons, accepting a fit only where every form it generates is in the SJP list | 53.0% of a 3,000-word residual sample |

Together they would put coverage near 93–94% with no model involved. The
numbers stand if the residual becomes worth attacking; the shipped answer is
`nieznane`.

Odmiana and part of speech come from the sources alone: SGJP is a hand-built
gold resource, and a generative step over it can only add error. The channel a
later model proposal would take is `lexica.maintenance.overrides`, which reads
a gitignored YAML per dictionary, fails loudly on a form absent from the
dictionary and on a duplicate marker, and is reviewed by hand before it is
accepted. A reading that arrived that way carries `AnalysisSource.OVERRIDE`, so
the panel can say where it came from. The sibling ContextGraph repository runs
an LLM pipeline whose shape suits this one: a client protocol with structured
output, a content-addressed response cache keyed on prompt and schema, and
per-stage input digests in a manifest, which together keep a rerun
byte-identical.

## Determinism

Every step is a lookup or a pure table: analysis is a dictionary lookup,
classification is the segment table in `lexica.grammar`, assembly is grouping.
The same inputs produce the same artifacts byte for byte, which is what makes
the pinned releases in `wordtable.releases` a complete description of a build.

## What the tests hold

`tests/specimens/oracle.yaml` states what Polish grammar requires of 159
hand-picked homonyms and irregulars, written in the project's own vocabulary
(`dopełniacz`, `męskoosobowy`, `odsłownik`) rather than in SGJP tags, so it
tests the mapping as well as the readings. Each specimen may require readings,
require forms inside a paradigm, deny readings, and deny forms. `BRONIĄ` must
read as both *broń* in narzędnik and *bronić* in the third person plural;
`ZAMEK` must carry both *zamka* and *zamku*; `ZIELONY` must never be read under
the lexeme *najzieleńszy*.

The set of claims stays open by design. SGJP holds readings beyond what
knowing Polish predicts — *warto* as the wołacz of *warta*, *koga* as a
medieval ship, the names of the letters — so enumerating them would copy the
analyser into the test that checks it.

## Attribution

| Source | Terms | Credit |
| --- | --- | --- |
| SJP game word list | GPL 2 and CC BY 4.0; CC BY 4.0 is the option taken | sjp.pl |
| Morfeusz 2 and the bundled SGJP inflectional data | BSD-2-Clause | Zygmunt Saloni et al., SGJP |
| PoliMorf | BSD-2-Clause | ZIL IPI PAN |

CC BY 4.0 carries attribution and no share-alike, so the compiled artifacts and
the game around them stay under their own terms. The credit belongs in the game
and in the repository.
