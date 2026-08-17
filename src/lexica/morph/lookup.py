from enum import StrEnum
from typing import TypeVar

from lexica.morph.mapping import build_analysis
from lexica.morph.models import MorphSource, MorphTags
from wordcore.lexicon.morph import MorphLexicon

_EnumValue = TypeVar("_EnumValue", bound=StrEnum)


def lookup_lines(lexicon: MorphLexicon, word: str) -> tuple[str, ...]:
    surface = word.upper()
    if not lexicon.judge(surface).allowed:
        return (f"{surface}: absent from the dictionary",)
    if not lexicon.class_infos(surface):
        return (f"{surface}: unclassified",)

    lines = [surface]
    for lemma, source, tag in lexicon.analysis_rows(surface):
        analysis = build_analysis(surface, lemma, tag, MorphSource(source), ())
        lines.append(f"  {analysis.part.value} · {analysis.lemma} · {tag}")
        summary = _tag_summary(analysis.tags)
        if summary:
            lines.append(f"    {summary}")
    return tuple(lines)


def _tag_summary(tags: MorphTags) -> str:
    fields: list[str] = []
    if tags.cases:
        fields.append(f"przypadki: {_joined(tags.cases)}")
    if tags.number is not None:
        fields.append(f"liczba: {tags.number.value}")
    if tags.genders:
        fields.append(f"rodzaje: {_joined(tags.genders)}")
    if tags.person is not None:
        fields.append(f"osoba: {tags.person.value}")
    if tags.tense is not None:
        fields.append(f"czas: {tags.tense.value}")
    if tags.mood is not None:
        fields.append(f"tryb: {tags.mood.value}")
    if tags.aspects:
        fields.append(f"aspekty: {_joined(tags.aspects)}")
    if tags.degree is not None:
        fields.append(f"stopień: {tags.degree.value}")
    if tags.verb_form is not None:
        fields.append(f"forma: {tags.verb_form.value}")
    if tags.numeral_type is not None:
        fields.append(f"typ liczebnika: {tags.numeral_type.value}")
    if tags.pronoun_type is not None:
        fields.append(f"typ zaimka: {tags.pronoun_type.value}")
    if tags.negation is not None:
        fields.append(f"negacja: {'tak' if tags.negation else 'nie'}")
    if tags.deprecative:
        fields.append("forma deprecjatywna")
    if tags.extras:
        fields.append(f"dodatki: {', '.join(sorted(tags.extras))}")
    return " · ".join(fields)


def _joined(values: frozenset[_EnumValue]) -> str:
    return ", ".join(sorted(value.value for value in values))
