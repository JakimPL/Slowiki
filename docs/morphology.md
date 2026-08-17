# Polish morphology — grammar reference and data sources

This document records the grammatical model the morphology pipeline encodes and
the survey of data sources that supply complete Polish inflection data. Facts
taken from this repository are verified; facts about external sources carry a
`pending` marker until Phase 0 of the implementation confirms licenses, URLs,
and counts on the web.

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

The pipeline additionally uses `OTHER` for tokens outside the canonical ten
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

A finite-state morphological analyzer from IPI PAN
(https://sgjp.pl/morfeusz/). The underlying dictionary is the Słownik
gramatyczny języka polskiego (SGJP) by Zygmunt Saloni et al., which lists every
inflected form of every paradigm explicitly. Analyses arrive as
`form, tags, lemma` triples with Morfeusz tags such as `subst:sg:inst:f`;
homonymic surfaces yield several interpretations. The library also generates
paradigm forms from a lemma.

Distributions: C/C++ library, CLI, and a Python binding published as
`morfeusz2` on PyPI with the dictionary bundled.

- License of the library and of the SGJP dictionary: `pending` — Phase 0
  verification (the terms changed across SGJP editions).
- Coverage (millions of forms, ≈4M): `pending` — Phase 0 measurement.
- Role: primary analysis source, option A.

### PoliMorf

A merged inflectional dictionary from ZIL IPI PAN
(https://zil.ipipan.waw.pl/PoliMorf), combining SGJP with further sources and
a Morfeusz-compatible tagset. Downloads are tabular text
(form / lemma / tag columns); homonymic lemmas carry qualifiers
(lemma:qualifier syntax: `pending` — Phase 0 verification of the exact
format).

- License: `pending` — believed CC BY-SA; Phase 0 verification.
- Role: primary analysis source, option B, readable with the standard library;
  also a cross-check for option C (Morfeusz + PoliMorf agreement).

### Morfologik polish.dict

Binary FSA morphological dictionary for the Java Morfologik library
(https://github.com/morfologik/morfologik-stemming), built from SGJP/PoliMorf
data and used by LanguageTool. The library is BSD-licensed; the dictionary
license follows its sources (`pending`). Python consumption requires a reader
for the FSA format; the tabular sources it derives from are preferable.

### WSJP — Wielki słownik języka polskiego PAN

The PAN dictionary (https://wsjp.pl) records full inflection tables per
lexeme. A machine-readable API is reported to exist (`pending` — Phase 0
verification of endpoint, response format, bulk-access policy, and license).
Role: cross-check for paradigm-level data and, in the future, sense-level
homonym disambiguation.

### Wiktionary PL and kaikki.org

Polish Wiktionary stores per-lemma inflection tables (odmiana templates)
under CC BY-SA. kaikki.org serves machine-readable Wiktionary extracts,
including Polish (`pending` — Phase 0 verification of the Polish dataset).
Role: cross-check and few-shot material for any future review tool.

### Taggers (cross-check only)

spaCy `pl_core_news_sm/md/lg` (trained on NKJP), KRNNT, and Concraft-pl assign
POS tags to running text. They tag forms; the paradigm sources above enumerate
complete paradigms. Useful as an independent cross-check for disputed
classifications. Licenses: `pending`.

### Comparison

| Source | Paradigm-complete | Homonyms | Format | Python access | License | Role |
|---|---|---|---|---|---|---|
| SJP słowa.txt | n/a | n/a | plain text | existing loader | GPL 2 + CC BY 4.0 | ground truth |
| Morfeusz 2 / SGJP | yes | interpretations | FSA binary | `morfeusz2` pip | `pending` | option A |
| PoliMorf | yes | lemma qualifiers | tabular text | stdlib | `pending` | option B / cross-check |
| Morfologik polish.dict | yes | via source | binary FSA | custom reader | `pending` | reference |
| WSJP | yes | senses | API | HTTP | `pending` | cross-check |
| Wiktionary / kaikki | most | senses | JSONL | stdlib | CC BY-SA | cross-check |
| Taggers (spaCy, KRNNT, Concraft) | no | no | models | pip | `pending` | dispute check |

## Morfeusz tagset → PartOfSpeech mapping (draft)

The mapping is a deterministic table, unit-tested in Phase 1. The tag list
below is a draft; Phase 0 confirms it against the downloaded dictionary data.

| Tag prefix | PartOfSpeech | Notes |
|---|---|---|
| subst | RZECZOWNIK | + case, number, gender |
| dep | RZECZOWNIK | deprecjatywna forma |
| adj | PRZYMIOTNIK | + case, number, gender, degree |
| adja, adjp | PRZYMIOTNIK | subtypes: `pending` verification |
| adv | PRZYSŁÓWEK | + degree where present |
| num | LICZEBNIK | + type (główny, porządkowy, zbiorowy) |
| ppron12, ppron3, siebie | ZAIMEK | + subtype |
| prep | PRZYIMEK | + governed case |
| conj | SPÓJNIK | |
| qub | PARTYKUŁA | |
| interj | WYKRZYKNIK | |
| fin, bedzie, aglt, praet, impt, imps, inf, pcon, pant, pact, ppas, ger | CZASOWNIK | + form subtype, aspect, etc. |
| pred | CZASOWNIK | czasownik niewłaściwy |
| brev, burk | OTHER | skrót (`burk`: `pending`) |
| xx, ign | OTHER | unrecognized: reported, never silently guessed |

Tag dimensions: case nom/gen/dat/acc/inst/loc/voc; number sg/pl; gender
m1/m2/m3/f/n; person pri/sec/ter; degree pos/com/sup; aspect imperf/perf;
negation aff/neg.

## Coverage expectations

The SJP list contains proper-noun-derived adjectives (e.g. `aalborscy`),
archaic, dialectal, and regional forms that morphological dictionaries may not
cover. Forms that receive no analysis become `UNKNOWN` entries and appear in
the report; the report is the control surface for coverage.

Phase 0 measures:

- the share of the 3,240,429 forms with at least one analysis,
- the per-POS distribution,
- the homonym multiplicity distribution (forms with 2+ classes),
- license compatibility of each candidate source with GPL 2 / CC BY 4.0.

## Phase 0 verification checklist

Confirm on the web before Phase 2:

- Morfeusz 2: license of the library, license of the bundled SGJP dictionary,
  total analysed form count, homonym representation in output.
- `morfeusz2` PyPI package: maintainer, bundled dictionary version, platform
  wheels.
- PoliMorf: license, download URLs, exact column order, homonym qualifier
  syntax, entry count.
- Morfologik polish.dict: license of the dictionary file.
- WSJP: API documentation URL, response shape, bulk-access policy, license.
- kaikki.org: Polish dataset availability and contents.
- spaCy pl models, KRNNT, Concraft-pl licenses.
