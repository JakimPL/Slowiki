from pathlib import Path
from typing import Final

from lexica.artifact.words import read_word_list
from lexica.build.coverage import Coverage, CoverageResult, coverage_of
from lexica.lore.sources import LoreSources
from lexica.names import DictionaryName
from lexica.sources.sgjp import build_morfeusz_engine
from wordtable.lexicons import compile_dictionary
from wordtable.overrides import load_overrides
from wordtable.paths import dictionary_coverage, dictionary_unread
from wordtable.rescue import load_rescue

_INDENT: Final = 2
_PERCENT: Final = 100.0
_LABEL_WIDTH: Final = 11


def report_coverage(name: DictionaryName) -> CoverageResult:
    lexicon = read_word_list(compile_dictionary(name))
    sources = LoreSources(
        engine=build_morfeusz_engine(),
        rescue=load_rescue(name),
        overrides=load_overrides(name, lexicon),
    )
    result = coverage_of(name, lexicon.words, sources)
    _write_coverage(dictionary_coverage(name), result.coverage)
    _write_unread(dictionary_unread(name), result.unread)
    return result


def summary_of(coverage: Coverage) -> str:
    shares = {
        "read": coverage.read,
        "rescued": coverage.rescued,
        "overridden": coverage.overridden,
        "residual": coverage.residual,
    }
    lines = (
        f"{coverage.dictionary}: {coverage.forms} forms read against {coverage.dict_id}",
        *(
            f"  {_labelled(label)}{_counted(count, coverage.forms)}"
            for label, count in shares.items()
        ),
        f"  {_labelled('lexemes')}{coverage.lexemes}",
    )
    return "\n".join(lines)


def _labelled(label: str) -> str:
    return label.ljust(_LABEL_WIDTH)


def _counted(part: int, whole: int) -> str:
    return f"{part} ({part * _PERCENT / whole:.2f}%)" if whole > 0 else f"{part}"


def _write_coverage(destination: Path, coverage: Coverage) -> None:
    destination.write_text(coverage.model_dump_json(indent=_INDENT) + "\n", encoding="utf-8")


def _write_unread(destination: Path, unread: tuple[str, ...]) -> None:
    destination.write_text("".join(f"{form}\n" for form in unread), encoding="utf-8")
