# Polish morphology — grammar reference and data sources

This document records the grammatical model the morphology pipeline encodes and
the survey of data sources that supply complete Polish inflection data. All
license, format, and coverage facts below were verified on 2026-08-17 during
Phase 0; measurement numbers come from runs in this repository.

## Purpose

The morphology subsystem produces, for every word in the game dictionary:

- a classification into Polish parts of speech (części mowy, Polish
  nomenclature), with grammatical tags for each inflected form,
- equivalence classes of words and their inflected variants (deklinacja,
  koniugacja, stopniowanie),
- robust handling of homonyms: one surface form may belong to several classes,
  and one class may share forms with other classes.

A class groups a lemma, its part of speech, and its inflection pattern with all
of its inflected forms. Classes describe paradigms; the pipeline performs
variant recognition, explicitly separating it from lemmatization and stemming.

## Polish grammar reference

### Części mowy

The canonical school set divides into odmienne (inflected) and nieodmienne
(uninflected) parts of speech.

| Polish name | English gloss | Inflected | Inflection kinds |
|---|---|---|---|
| RZECZOWNIK | noun | odmienna | deklinacja: przypadki, liczby, rodzaje |
| PRZYMIOTNIK | adjective | odmienna | deklinacja: przypadki, liczby, rodzaje; stopniowanie |
| LICZEBNIK | numeral | odmienna | deklinacja: przypadki, liczby, rodzaje |
| ZAIMEK | pronoun | odmienna | deklinacja: przypadki, liczby, rodzaje |
| CZASOWNIK | verb | odmienna | koniugacja: osoby, liczby, czasy, tryby, aspekt, rodzaje |
| PRZYSŁÓWEK | adverb | nieodmienna | stopniowanie (partially) |
| PRZYIMEK | preposition | nieodmienna | rekcja (governs a case) |
| SPÓJNIK | conjunction | nieodmienna | — |
| PARTYKUŁA | particle | nieodmienna | — |
| WYKRZYKNIK | interjection | nieodmienna | — |

The pipeline additionally uses `INNY` for tokens outside the canonical ten
(skróty, symbole), so that every dictionary entry carries a label while the
canonical classification stays pure.

### Deklinacja

**Przypadki** (cases), with their traditional questions:

| Case | Polish | Question |
|---|---|---|
| NOM | mianownik | kto? co? |
| GEN | dopełniacz | kogo? czego? |
| DAT | celownik | komu? czemu? |
| ACC | biernik | kogo? co? |
| INST | narzędnik | (z) kim? (z) czym? |
| LOC | miejscownik | (o) kim? (o) czym? |
| VOC | wołacz | o! |

**Liczby**: pojedyncza (sg), mnoga (pl).

**Rodzaje** (genders). The SGJP/Morfeusz tagset uses five:

| Tag | Polish | English |
|---|---|---|
| m1 | męskoosobowy | personal masculine |
| m2 | męskozwierzęcy | animate masculine |
| m3 | męskorzeczowy | inanimate masculine |
| f | żeński | feminine |
| n | nijaki | neuter |

Nouns, adjectives, numerals, and pronouns inflect through all seven cases,
both numbers, and the genders they admit. Nouns additionally carry a
deprecjatywna form (e.g. `chłopy`, `dziady`) for m1 nouns.

### Koniugacja

Verbs inflect through:

- **Osoby**: 1 (pri), 2 (sec), 3 (ter).
- **Liczby**: pojedyncza, mnoga.
- **Czasy**: teraźniejszy (niedokonane only), przeszły, przyszły (prosty for
  dokonane, złożony for niedokonane).
- **Tryby**: oznajmujący (indicative), rozkazujący (imperative),
  przypuszczający (conditional).
- **Aspekt**: dokonany (perf), niedokonany (imperf).
- **Rodzaj**: past-tense forms carry m1/m2/m3/f/n.
- **Formy nieosobowe**:
  - bezokolicznik (infinitive),
  - bezosobnik (-no, -to),
  - imiesłów przymiotnikowy czynny (-ący),
  - imiesłów przymiotnikowy bierny (-ny, -ty),
  - imiesłów przysłówkowy współczesny (-ąc),
  - imiesłów przysłówkowy uprzedni (-łszy, -wszy),
  - odsłownik (rzeczownik odczasownikowy, -nie, -cie).
- **Ruchome końcówki**: bym, byś, by, byśmy, byście (agglutinants attached to
  the conditional mood).

Predykatywy (`trzeba`, `można`, `warto`) are czasowniki niewłaściwe; the
pipeline classifies them as CZASOWNIK with a subtype.

### Stopniowanie

Adjectives and some adverbs inflect through degrees: równy (positive),
wyższy (comparative), najwyższy (superlative). A subset forms degrees
descriptively (bardziej, mniej).

### Liczebniki

Types: główny (cardinal), porządkowy (ordinal), zbiorowy (collective),
ułamkowy (fractional), nieokreślony (indefinite). They inflect through cases,
numbers, and genders.

### Zaimki

Types: osobowy (personal), zwrotny (reflexive: się, siebie), dzierżawczy
(possessive), wskazujący (demonstrative), pytajny (interrogative), względny
(relative), nieokreślony (indefinite), przeczący (negative).

### Przyimki

Przyimki are uninflected; each governs a case (rekcja): biernik, dopełniacz,
celownik, miejscownik, or narzędnik.

## Homonymy

Paradigm-level homonyms share a surface form across distinct paradigms. The
pipeline represents each paradigm as a separate class, so one surface maps to
several classes.

| Surface | Class A | Class B |
|---|---|---|
| bronią | broń, RZECZOWNIK, narzędnik lp f | bronić, CZASOWNIK, 3 os. lm ter. |
| morze / może | morze, RZECZOWNIK, mianownik lp n | móc, CZASOWNIK, 3 os. lp ter. |
| zamek | zamek¹ (budowla), dopełniacz `zamku` | zamek² (błyskawiczny), dopełniacz `zamka` |
| rząd | rząd¹ (władza), dopełniacz `rządu` | rząd² (szereg), dopełniacz `rzędu` |
| bal | bal¹ (belka), dopełniacz `bala` | bal² (zabawa), dopełniacz `balu` |
| marsz | marsz¹ (chód), dopełniacz `marszu` | marsz² (utwór), dopełniacz `marsza` |
| wina | wina¹ (przewinienie) | wino (wina = lm mianownik) |
| drogą | droga, RZECZOWNIK, narzędnik lp | drogi, PRZYMIOTNIK, narzędnik lp f |

Sense homonyms whose paradigms coincide (e.g. `klucz` as wrench and key) share
one class: the class key is lemma + part of speech + inflection pattern, so
identical paradigms merge by construction. Sense-level distinctions (WSJP,
Wiktionary) remain out of scope.

## Data sources

### Ground truth: the SJP game list

`dictionaries/sjp-20260803.zip` contains `slowa.txt`: 3,240,429 lines, one
lowercase Polish word per line, sorted, UTF-8 with CRLF terminators; inflected
forms included. License: GPL 2 and CC BY 4.0. Source: https://sjp.pl/sl/growy/
(verified in this repository, see `docs/dictionaries.md`). The list defines
game validity; morphology annotates it.

### Morfeusz 2 with the SGJP dictionary

A finite-state morphological analyzer from IPI PAN (https://morfeusz.sgjp.pl/).
The bundled dictionary is the Słownik gramatyczny języka polskiego (SGJP) by
Zygmunt Saloni et al., which lists every inflected form of every paradigm
explicitly. The analyzer also generates the full paradigm of a lemma.

Verified in Phase 0 (2026-08-17):

- License: the program and the bundled inflectional data (SGJP and PoliMorf
  data) ship under the 2-clause BSD license
  (http://morfeusz.sgjp.pl/doc/license/). The full SGJP text is a separate
  resource with separate terms; the analysis data is BSD-2-Clause.
- Python binding: `morfeusz2` on PyPI, version 1.99.15 (wheel dated
  2026-06-01), cp310-abi3 wheels for Linux, macOS, and Windows.
- Bundled dictionary identity: `pl.sgjp.sgjp-2026.06.01`.
- Output: one tuple per interpretation, `(orth, lemma, tag, names,
  qualifiers)`, e.g. `('bronią', 'broń', 'subst:sg:inst:f', ['nazwa_pospolita'], [])`.
- Homonyms: paradigm-level homonymic lemmas carry pattern-qualified names,
  e.g. `zamek:Sm3~a` (dopełniacz `zamka`) versus `zamek:Sm3~u` (dopełniacz
  `zamku`); usage qualifiers arrive in the qualifiers list (e.g. `muz.`).
- Unrecognized forms yield a single interpretation tagged `ign`.
- Throughput: ≈29,000 words/s in Python; the full 3,240,429-form pass takes
  ≈110 s.
- Coverage: 2,696,531 forms (83.22%) receive at least one real analysis;
  1,220,280 forms (37.66%) receive multiple interpretations, with up to 48
  interpretations per form.

Role: primary analysis source.

### PoliMorf

A merged inflectional dictionary from ZIL IPI PAN
(https://zil.ipipan.waw.pl/PoliMorf), combining SGJP with further sources.
It ships beside every Morfeusz release. Verified 2026-08-22:

- License: the source data and the resulting resource ship under the
  2-clause BSD license.
- Download: `https://download.sgjp.pl/morfeusz/20260726/polimorf-20260726.tab.gz`;
  45.2 MB compressed, 8,505,529 rows, dictionary id
  `pl.waw.ipipan.polimorf-2026.07.27`, sha256
  `d0315301beb4820577c8e04c885044feb852a72c865ce62e5e0a1836344e078e`.
- Format: a copyright preamble, then five tab-separated columns
  `form<TAB>lemma<TAB>tag<TAB>name<TAB>qualifiers`, e.g.
  `Aalborg<TAB>Aalborg<TAB>subst:sg:nom.acc:m3<TAB>nazwa_geograficzna<TAB>zwykle_lp`.
  A row carries exactly five columns; the preamble carries other arities.
- Tagset: the 2026 SGJP tagset, the same one Morfeusz answers in. All 714
  distinct tags read in `lexica.grammar` under `TagsetDialect.SGJP` with zero
  unmapped segments.
- Homonyms: lemma-level rows merge paradigm-level homonyms (`zamek` has one
  row set, while the 2026 SGJP separates `zamek:Sm3~a` and `zamek:Sm3~u`),
  so a rescued form carries a reading and holds no generated paradigm.
- Coverage: rescues 205,151 of the 543,898 SGJP-unknown forms (37.72%),
  carrying 309,816 (lemma, tag) rows.

Role: supplementary rescue source for SGJP-unknown forms, flagged by source
in the compiled artifact; combined coverage reaches 89.55%.

### Morfologik polish.dict

Binary FSA morphological dictionary for the Java Morfologik library
(https://github.com/morfologik/morfologik-stemming), built from SGJP/PoliMorf
data and used by LanguageTool. The library ships under the BSD-3-Clause
license (verified on GitHub, 2026-08-17). Python consumption requires a reader
for the FSA format; the tabular sources it derives from are preferable.

### WSJP — Wielki słownik języka polskiego PAN

The PAN dictionary (https://wsjp.pl) records full inflection tables per
lexeme. A machine-readable API is reported to exist; the site returned HTTP
403 to plain clients during Phase 0 verification, so endpoint, response
format, bulk-access policy, and license remain to confirm. Role: future
cross-check and sense-level homonym disambiguation.

### Wiktionary PL and kaikki.org

Polish Wiktionary stores per-lemma inflection tables (odmiana templates)
under CC BY-SA. kaikki.org serves machine-readable Wiktionary extracts; the
Polish index exists (https://kaikki.org/dictionary/Polish/, verified
2026-08-17). Role: cross-check and few-shot material for any future review
tool.

### Taggers (cross-check only)

spaCy `pl_core_news_sm/md/lg` (trained on NKJP), KRNNT, and Concraft-pl assign
POS tags to running text. They tag forms; the paradigm sources above enumerate
complete paradigms. Useful as an independent cross-check for disputed
classifications. Licenses: to confirm when a cross-check tool is built.

### Comparison

| Source | Paradigm-complete | Homonyms | Format | Python access | License | Role |
|---|---|---|---|---|---|---|
| SJP słowa.txt | n/a | n/a | plain text | existing loader | GPL 2 + CC BY 4.0 | ground truth |
| Morfeusz 2 / SGJP 2026.06.01 | yes | pattern-qualified lemmas | FSA binary | `morfeusz2` pip | BSD-2-Clause | primary |
| PoliMorf 2026.07.27 | yes | lemma-level (merges paradigms) | tabular text | stdlib | BSD-2-Clause | rescue source |
| Morfologik polish.dict | yes | via source | binary FSA | custom reader | BSD-3-Clause | reference |
| WSJP | yes | senses | API | HTTP | to confirm | future cross-check |
| Wiktionary / kaikki | most | senses | JSONL | stdlib | CC BY-SA | cross-check |
| Taggers (spaCy, KRNNT, Concraft) | no | no | models | pip | to confirm | dispute check |

## Morfeusz tagset → PartOfSpeech mapping (measured)

The mapping is a deterministic table, unit-tested in Phase 1. Prefixes below
come from the full-corpus pass over słowa.txt with the bundled
`pl.sgjp.sgjp-2026.06.01` dictionary; counts sum interpretations (one form may
carry several).

| Tag prefix | PartOfSpeech | Interpretations | Notes |
|---|---|---|---|
| subst | RZECZOWNIK | 723,526 | case, number, gender |
| depr | RZECZOWNIK | 10,801 | deprecjatywna forma |
| adj | PRZYMIOTNIK | 1,190,005 | case, number, gender, degree |
| adjp | PRZYMIOTNIK | 6,232 | poprzyimkowy, recorded as a quality |
| adjc | PRZYMIOTNIK | 11 | forma predykatywna (wart, gotów) |
| adv | PRZYSŁÓWEK | 26,141 | degree where present |
| comp | SPÓJNIK | 166 | spójnik podrzędny (by:M, to:M); the conditional clitic is `by:T part` |
| num | LICZEBNIK | 569 | główny; collective forms carry `:col` → ZBIOROWY |
| frag | LICZEBNIK | 90 | fragment of a multiword numeral |
| ppron12, ppron3, siebie | ZAIMEK | 100 | osobowy, zwrotny |
| prep | PRZYIMEK | 167 | governed case |
| conj | SPÓJNIK | 72 | |
| part | PARTYKUŁA | 297,406 | the 2026 tagset names particles `part` (classic `qub`) |
| interj | WYKRZYKNIK | 378 | |
| fin, bedzie, aglt, praet, cond, impt, imps, inf, pcon, pant, pact, ppas, ger | CZASOWNIK | 2,193,530 | verb form, aspect, person, tense; `cond` arrives with composite past forms |
| winien | CZASOWNIK | 56 | defective verb (winien/powinien) |
| pred | CZASOWNIK | 30 | czasownik niewłaściwy |
| brev | INNY | 24 | skrót |
| romandig | INNY | 3 | Roman numeral |
| ign, xx | INNY | — | unrecognized → UNKNOWN report |

Liczebniki porządkowe (piąty, drugi) carry the adjective tagset (`adj` with
the lemma qualifier `:A`) and classify as PRZYMIOTNIK; the school-level
ordinal reading is a lemma-level refinement.

## Tag segment inventory (measured, 2026-08-19)

The closed vocabulary in `lexica.grammar` comes from a full pass over
słowa.txt (3,240,429 forms) in both analyzer modes and over the whole PoliMorf
0.6.7 table (6,578,142 rows, every row four fields). Every distinct tag each
source can produce parses: **576** SGJP tags in the default mode, **645** in the
composite mode, **574** PoliMorf tags, with zero unrecognised segments. A
segment outside the table refuses the tag and names the dialect.

| Dimension | SGJP 2026 codes | PoliMorf classic codes |
|---|---|---|
| case | nom gen dat acc inst loc voc | same |
| number | sg pl | same |
| gender | m1 m2 m3 f n | m1 m2 m3 f n1 n2 p1 p2 p3 `_` |
| person | pri sec ter | same |
| aspect | imperf perf | same |
| degree | pos com sup | same |
| negation | aff neg | same |
| quality | akc nakc praep npraep agl nagl wok nwok congr rec col ncol pt pun npun | akc nakc praep npraep agl nagl wok nwok congr rec comp |

Dotted segments state alternatives on one dimension and arrive on every
dimension a source uses them for: `nom.acc.voc` (case), `m1.m2.m3` (gender),
`imperf.perf` (aspect), `akc.nakc` and `congr.rec` and `praep.npraep`
(quality), and **`sg.pl`** (number, 1,540 interpretations over nouns and
numerals). Number is therefore a set, as case, gender and aspect already were.

The classic PoliMorf gender codes read into the 2026 five-gender system:
`n1` and `n2` are NIJAKI, `p1` is MĘSKOOSOBOWY, `p2` and `p3` are NIJAKI (the
treatment SGJP gives pluralia tantum), and `_` states no gender. The PoliMorf
segment `comp` on a numeral and the SGJP prefix `numcomp` both state the
quality ZŁOŻONY, so a compound-forming numeral reads the same either way.

### Composite past forms (measured, both modes)

`morfeusz2.Morfeusz(praet="composite")` composes the past tense instead of
splitting it into a stem and an agglutinate:

| Reading | Default mode | Composite mode |
|---|---|---|
| praet interpretations | 512,301 | 278,389 |
| aglt interpretations | 282,950 | 182 |
| cond interpretations | — | 233,900 |
| praet carrying a person | none | 278,389 (all) |
| distinct tags | 576 | 645 |

`biegłem` reads as `praet:sg:m1.m2.m3:pri:imperf` with the person restored, and
`zrobiłbym` reads as `cond:sg:m1.m2.m3:pri:perf` — a real conditional, where the
default mode leaves a past form beside a movable ending. The grammar vocabulary
carries both readings: `cond` states the mood PRZYPUSZCZAJĄCY and the verb form
FORMA_PRZYPUSZCZAJĄCA, and `aglt` states the movable ending without claiming a
mood of its own.

### Qualifiers (measured over słowa.txt)

SGJP answers with two vocabularies: **26** name categories (`nazwa_pospolita`
711,240 interpretations, `nazwa_geograficzna` 4,180, `nazwisko` 16,347, `imię`
1,323, and 22 rarer ones) and **533** label strings built from **119** atoms
joined by commas (`daw.,char.`). PoliMorf answers with **12** name categories
(`pospolita`, `nazwisko`, `imię`, `geograficzna`, `określenie dodatkowe`, and
seven more). `lexica.grammar.qualifier` splits a joined label and types each
code as a name or a qualifier.

## Measured coverage (Phase 0, 2026-08-17)

Measured over the full słowa.txt (3,240,429 forms) with morfeusz2
(`pl.sgjp.sgjp-2026.06.01`, ≈110 s):

| Metric | Value |
|---|---|
| Classified by SGJP 2026 | 2,696,531 (83.22%) |
| SGJP-unknown | 543,898 (16.78%) |
| Rescued by PoliMorf 0.6.7 | 200,451 (36.85% of SGJP-unknown) |
| Combined classified | 2,896,982 (89.40%) |
| Remaining UNKNOWN | 343,447 (10.60%) |
| Forms with multiple interpretations | 1,220,280 (37.66%) |
| Maximum interpretations per form | 48 |
| Unique class keys (lemma + tag prefix) | 361,664 |

Unknown forms concentrate in proper-noun-derived adjectives (`aalborscy`,
`abadański`) and other formations absent from both dictionaries; PoliMorf
rescues many proper-derived forms. The remaining forms become `UNKNOWN`
entries in the report. Case folds cleanly: the analyzer classifies lowercase
and uppercase input identically (verified on a 10k sample).

### Analysis pipeline run (Phase 2, full corpus)

`lexica analyze --polimorf dictionaries/sources/PoliMorf-0.6.7.tab.gz` over
all 3,240,429 forms:

| Metric | Value |
|---|---|
| Classes assembled | 201,821 |
| Classes per POS | rzeczownik 86,223 · przymiotnik 64,132 · przysłówek 25,727 · czasownik 24,728 · wykrzyknik 378 · partykuła 243 · liczebnik 205 · przyimek 106 · spójnik 46 · zaimek 7 · inny 26 |
| Forms with multiple classes | 572,899 (17.68%) |
| Maximum classes per form | 7 |
| Wall time / peak memory | 9 min 7 s / 21.8 GB |

The 361,664 measured lemma+prefix pairs collapse to 201,821 classes because
one lemma carries several verb or adjective tag prefixes within a single
class. The zaimek count stays small because the tagset classifies most
pronouns as adjectives (a lemma-level refinement).

### Compiled artifact v2 (Phase 3, full corpus)

`lexica compile` over all 3,240,429 forms with PoliMorf rescue:

| Metric | Value |
|---|---|
| Compile wall time / peak memory | 3 min 51 s / 3.4 GB |
| Artifact size | 216 MB |
| Load time / resident memory | 7.7 s / 1.5 GB |
| Artifact contents | 3,240,429 surfaces, 201,821 classes, 343,447 UNKNOWN |

`BRONIĄ` resolves to both classes (`czasownik:BRONIĆ`, `rzeczownik:BROŃ`) with
correct bases; the surface index keeps `judge`/`has_prefix` at bisect speed.

## Source decision (Phase 0)

- Primary analysis source: morfeusz2 with the bundled SGJP 2026.06.01 —
  newest data, paradigm-level homonym separation through pattern-qualified
  lemmas, native paradigm generation.
- Supplementary rescue source: PoliMorf 0.6.7 tabular data for SGJP-unknown
  forms; analyses carry a `source` flag.
- Both sources ship under the 2-clause BSD license, compatible with the SJP
  list's GPL 2 / CC BY 4.0 terms for the compiled artifact.
- WSJP and kaikki remain cross-check options; WSJP returned HTTP 403 to plain
  clients.

## Phase 0 verification checklist — status

Completed on 2026-08-17:

- Morfeusz 2: license (BSD-2-Clause for program and inflectional data),
  PyPI package (`morfeusz2` 1.99.15), bundled dictionary
  (`pl.sgjp.sgjp-2026.06.01`), output shape, homonym representation
  (pattern-qualified lemmas), throughput, coverage.
- PoliMorf: license (BSD-2-Clause), download URL, row format, tagset
  differences, homonym merging behaviour, rescue coverage.
- Morfologik: library license (BSD-3-Clause).
- kaikki.org: Polish dictionary index exists.
- WSJP: API access remains to confirm; the site returned HTTP 403 to plain
  clients.
- Taggers (spaCy, KRNNT, Concraft-pl): licenses to confirm when a
  cross-check tool is built.
