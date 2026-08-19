from collections.abc import Sequence
from enum import StrEnum
from typing import Final

from wordcore.models.base import BaseFrozen

LABEL_SEPARATOR: Final = ","


class QualifierKind(StrEnum):
    NAZWA = "nazwa"
    KWALIFIKATOR = "kwalifikator"


class Qualifier(BaseFrozen):
    kind: QualifierKind
    code: str


def qualifiers_of(names: Sequence[str], labels: Sequence[str]) -> tuple[Qualifier, ...]:
    collected = [
        *_qualifiers(QualifierKind.NAZWA, names),
        *_qualifiers(QualifierKind.KWALIFIKATOR, labels),
    ]
    return tuple(dict.fromkeys(collected))


def _qualifiers(kind: QualifierKind, values: Sequence[str]) -> tuple[Qualifier, ...]:
    return tuple(Qualifier(kind=kind, code=code) for value in values for code in _codes(value))


def _codes(value: str) -> tuple[str, ...]:
    stripped = (code.strip() for code in value.split(LABEL_SEPARATOR))
    return tuple(code for code in stripped if len(code) > 0)
