from typing import Final

from lexica.lore.override import OverrideTable
from lexica.maintenance.overrides import parse_overrides
from lexica.names import DictionaryName
from wordcore.lexicon.protocol import Lexicon
from wordtable.paths import dictionary_overrides

_NO_OVERRIDES: Final[OverrideTable] = {}


def load_overrides(name: DictionaryName, lexicon: Lexicon) -> OverrideTable:
    path = dictionary_overrides(name)
    if not path.is_file():
        return _NO_OVERRIDES

    return parse_overrides(path, lambda form: lexicon.judge(form).allowed)
