import argparse
import random
from collections import Counter
from pathlib import Path
from typing import Final, Protocol

import yaml

from lexica.dictionaries.sjp import iter_sjp_words
from lexica.morph.sources.sgjp import Interpretation, head_interpretations

try:
    import morfeusz2  # type: ignore[import-untyped]
except ImportError as error:
    raise SystemExit("install the morphology extra: uv sync --extra morphology") from error

PROJECT_ROOT: Final = Path(__file__).resolve().parents[1]
_DEFAULT_ARCHIVE: Final = PROJECT_ROOT / "dictionaries" / "sjp-20260803.zip"
_DEFAULT_CORPUS: Final = PROJECT_ROOT / "dictionaries" / "specimens" / "specimens.yaml"
_DEFAULT_STRESS: Final = PROJECT_ROOT / "tests" / "specimens" / "stress.yaml"

_SEED: Final = 20260817
_POOL_SIZE: Final = 60000
_SAMPLE_TOTAL: Final = 4000
_MIN_QUOTA: Final = 2

_STRESS: Final[tuple[str, ...]] = (
    "aalborscy",
    "abadańscy",
    "aha",
    "ale",
    "bal",
    "bala",
    "balu",
    "bracia",
    "brat",
    "bronią",
    "by",
    "bym",
    "być",
    "był",
    "była",
    "byś",
    "bądź",
    "będzie",
    "chłop",
    "chłopi",
    "chłopy",
    "ci",
    "czytanie",
    "czytano",
    "czyżby",
    "człowiek",
    "dni",
    "dnia",
    "drogi",
    "drogą",
    "drugi",
    "drugiego",
    "dwa",
    "dwie",
    "dzieci",
    "dziecko",
    "dzień",
    "hej",
    "ich",
    "idąc",
    "imienia",
    "imię",
    "jeden",
    "jednego",
    "jego",
    "jest",
    "kocie",
    "kogo",
    "komu",
    "kot",
    "kota",
    "kotem",
    "kotu",
    "ksiądz",
    "księża",
    "kto",
    "którego",
    "który",
    "ku",
    "lat",
    "lata",
    "lub",
    "ludzie",
    "marsz",
    "marsza",
    "marszu",
    "milion",
    "morze",
    "może",
    "można",
    "mądry",
    "mądrzejszy",
    "męski",
    "nad",
    "najmądrzejszy",
    "najszybciej",
    "nasi",
    "nasz",
    "nie",
    "no",
    "noc",
    "nocy",
    "oczy",
    "ojej",
    "oka",
    "oko",
    "oraz",
    "panie",
    "panowie",
    "pary",
    "państwo",
    "pieniądz",
    "pieniądze",
    "pierwszy",
    "pisanie",
    "piąty",
    "pod",
    "polski",
    "polskiego",
    "przyjaciel",
    "przyjaciółka",
    "przyszedłszy",
    "psa",
    "psem",
    "psy",
    "robi",
    "robiono",
    "robiący",
    "robić",
    "robił",
    "rok",
    "roku",
    "rząd",
    "rządu",
    "rzędu",
    "ręce",
    "ręka",
    "setka",
    "siebie",
    "się",
    "sobie",
    "soli",
    "sto",
    "stołem",
    "stołu",
    "stół",
    "szybciej",
    "szybko",
    "sól",
    "są",
    "sąsiad",
    "sąsiedzi",
    "ta",
    "te",
    "ten",
    "to",
    "troje",
    "trzeba",
    "trzech",
    "trzy",
    "tydzień",
    "tygodnia",
    "tysiąc",
    "ucha",
    "ucho",
    "uczeń",
    "ucznia",
    "uczniowie",
    "uszy",
    "warto",
    "wina",
    "wino",
    "zamek",
    "zamka",
    "zamku",
    "zieleni",
    "zieleń",
    "zielony",
    "zrobiony",
)


class _Analyzer(Protocol):
    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]: ...

    def dict_id(self) -> str: ...


def load_dictionary_words(archive: Path) -> tuple[str, ...]:
    return tuple(word.lower() for word in iter_sjp_words(archive))


def analyse_word(analyzer: _Analyzer, word: str) -> list[Interpretation]:
    return [interpretation for _, _, interpretation in head_interpretations(analyzer.analyse(word))]


def real_interpretations(interpretations: list[Interpretation]) -> list[Interpretation]:
    return [
        interpretation
        for interpretation in interpretations
        if not interpretation[2].startswith(("ign", "xx"))
    ]


def tag_prefix(interpretation: Interpretation) -> str:
    return interpretation[2].split(":", 1)[0]


def bucket_words(pool: tuple[str, ...], analyzer: _Analyzer) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for word in pool:
        real = real_interpretations(analyse_word(analyzer, word))
        prefix = tag_prefix(real[0]) if real else "ign"
        buckets.setdefault(prefix, []).append(word)
    return buckets


def build_quotas(buckets: dict[str, list[str]]) -> dict[str, int]:
    quotas: dict[str, int] = {}
    total = sum(len(entries) for entries in buckets.values())
    for prefix, entries in sorted(buckets.items()):
        share = len(entries) / total
        quotas[prefix] = max(_MIN_QUOTA, min(len(entries), round(_SAMPLE_TOTAL * share)))
    adjust = _SAMPLE_TOTAL - sum(quotas.values())
    largest = max(buckets, key=lambda prefix: len(buckets[prefix]))
    quotas[largest] += adjust
    for prefix, entries in buckets.items():
        quotas[prefix] = min(quotas[prefix], len(entries))
    return quotas


def select_specimens(
    words: tuple[str, ...],
    analyzer: _Analyzer,
    stress: tuple[str, ...],
    rng: random.Random,
) -> tuple[str, ...]:
    pool = tuple(rng.sample(words, _POOL_SIZE))
    buckets = bucket_words(pool, analyzer)
    quotas = build_quotas(buckets)
    selected: list[str] = []
    for prefix, entries in sorted(buckets.items()):
        selected.extend(rng.sample(entries, quotas[prefix]))
    return tuple(sorted(set(selected) | set(stress)))


def collect_interpretations(
    words: tuple[str, ...],
    analyzer: _Analyzer,
) -> dict[str, list[Interpretation]]:
    return {word: analyse_word(analyzer, word) for word in words}


def unknown_specimens(all_interpretations: dict[str, list[Interpretation]]) -> int:
    return sum(
        1
        for interpretations in all_interpretations.values()
        if not real_interpretations(interpretations)
    )


def pos_counts(all_interpretations: dict[str, list[Interpretation]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for interpretations in all_interpretations.values():
        for interpretation in real_interpretations(interpretations):
            counts[tag_prefix(interpretation)] += 1
    return dict(sorted(counts.items()))


def dump_document(output: Path, document: dict[str, object]) -> None:
    body = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    if body is None:
        raise SystemExit(f"yaml serialization produced no output for {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="specimens")
    parser.add_argument("--archive", type=Path, default=_DEFAULT_ARCHIVE)
    parser.add_argument("--corpus", type=Path, default=_DEFAULT_CORPUS)
    parser.add_argument("--stress", type=Path, default=_DEFAULT_STRESS)
    args = parser.parse_args(argv)

    words = load_dictionary_words(args.archive)
    word_set = set(words)
    missing = [word for word in _STRESS if word not in word_set]
    if missing:
        raise SystemExit(f"stress words absent from the dictionary: {missing}")

    analyzer: _Analyzer = morfeusz2.Morfeusz()
    rng = random.Random(_SEED)
    selected = select_specimens(words, analyzer, _STRESS, rng)
    all_interpretations = collect_interpretations(selected, analyzer)
    unknown = unknown_specimens(all_interpretations)
    counts = pos_counts(all_interpretations)

    corpus_document: dict[str, object] = {
        "seed": _SEED,
        "dictionary": "sjp-20260803",
        "dictionary_file": "slowa.txt",
        "analyzer": "morfeusz2",
        "dict_id": analyzer.dict_id(),
        "sampling": "60k uniform pool, proportional-per-POS quotas, min 2, plus stress list",
        "specimen_count": len(selected),
        "unknown_specimens": unknown,
        "pos_counts": counts,
        "specimens": [
            {
                "word": word,
                "analyses": [list(interpretation) for interpretation in all_interpretations[word]],
            }
            for word in selected
        ],
    }
    dump_document(args.corpus, corpus_document)

    stress_words = [word for word in selected if word in set(_STRESS)]
    stress_document: dict[str, object] = {
        "seed": _SEED,
        "dictionary": "sjp-20260803",
        "analyzer": "morfeusz2",
        "dict_id": analyzer.dict_id(),
        "purpose": "hand-reviewable golden anchor; full corpus lives in dictionaries/specimens/ (gitignored)",
        "specimen_count": len(stress_words),
        "unknown_specimens": sum(
            1 for word in stress_words if not real_interpretations(all_interpretations[word])
        ),
        "specimens": [
            {
                "word": word,
                "analyses": [list(interpretation) for interpretation in all_interpretations[word]],
            }
            for word in stress_words
        ],
    }
    dump_document(args.stress, stress_document)
    print(
        f"{args.corpus}: {len(selected)} specimens; "
        f"{args.stress}: {len(stress_words)} stress specimens; {unknown} unknown"
    )


if __name__ == "__main__":
    main()
