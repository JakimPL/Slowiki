from collections import Counter
from collections.abc import Iterable
from typing import NamedTuple

from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.lore.analysis_source import AnalysisSource
from lexica.lore.lexeme_id import LexemeId
from lexica.lore.lookup import analyses_of
from lexica.lore.sources import LoreSources
from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen


class Coverage(BaseFrozen):
    dictionary: DictionaryName
    dict_id: str
    forms: int
    read: int
    rescued: int
    residual: int
    lexemes: int
    parts: dict[PartOfSpeech, int]


class CoverageResult(NamedTuple):
    coverage: Coverage
    unread: tuple[str, ...]


class _Tally(NamedTuple):
    forms: int
    read: int
    rescued: int
    lexemes: set[LexemeId]
    unread: list[str]


def coverage_of(
    dictionary: DictionaryName,
    words: Iterable[str],
    sources: LoreSources,
) -> CoverageResult:
    tally = _tallied(words, sources)
    return CoverageResult(
        coverage=Coverage(
            dictionary=dictionary,
            dict_id=sources.engine.dict_id(),
            forms=tally.forms,
            read=tally.read,
            rescued=tally.rescued,
            residual=len(tally.unread),
            lexemes=len(tally.lexemes),
            parts=_lexemes_by_part(tally.lexemes),
        ),
        unread=tuple(tally.unread),
    )


def _tallied(words: Iterable[str], sources: LoreSources) -> _Tally:
    lexemes: set[LexemeId] = set()
    unread: list[str] = []
    forms = 0
    read = 0
    rescued = 0
    for form in words:
        forms += 1
        analyses = analyses_of(sources, form)
        if len(analyses) == 0:
            unread.append(form)
            continue

        if analyses[0].source is AnalysisSource.SGJP:
            read += 1
        else:
            rescued += 1
        lexemes.update(analysis.lexeme for analysis in analyses)

    return _Tally(forms=forms, read=read, rescued=rescued, lexemes=lexemes, unread=unread)


def _lexemes_by_part(lexemes: Iterable[LexemeId]) -> dict[PartOfSpeech, int]:
    counts = Counter(lexeme.part for lexeme in lexemes)
    return {part: counts[part] for part in PartOfSpeech if counts[part] > 0}
