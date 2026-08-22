from collections.abc import Iterable
from pathlib import Path

from lexica.lore.rescue import RescueTable
from lexica.sources.polimorf import rescue_rows
from lexica.sources.sgjp import MorfeuszEngine, analyse_word


def rescue_table_of(
    words: Iterable[str],
    engine: MorfeuszEngine,
    polimorf_path: Path,
) -> RescueTable:
    return rescue_rows(polimorf_path, unreadable_forms(words, engine))


def unreadable_forms(words: Iterable[str], engine: MorfeuszEngine) -> frozenset[str]:
    return frozenset(word for word in words if len(analyse_word(engine, word)) == 0)
