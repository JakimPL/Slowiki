from pathlib import Path

from lexica.names import DictionaryName
from wordcore.models.base import BaseFrozen
from wordtable.names import PresetName
from wordtable.paths import CONFIGURATION_SCHEMES_PATH
from wordtable.resolved import ResolvedScheme
from wordtable.rules import MIN_SEATS
from wordtable.scheme import SchemeConfig, load_scheme
from wordtable.settling import resolve_table, seats_admitted


class Offering(BaseFrozen):
    name: PresetName
    dictionary: DictionaryName
    min_players: int
    max_players: int


def list_schemes(directory: Path) -> dict[str, SchemeConfig]:
    schemes_dir = directory / CONFIGURATION_SCHEMES_PATH
    return {
        path.stem: load_scheme(directory, path.stem) for path in sorted(schemes_dir.glob("*.yaml"))
    }


def offerings(directory: Path) -> tuple[Offering, ...]:
    return tuple(
        _offering(resolve_table(directory, scheme, None))
        for scheme in list_schemes(directory).values()
    )


def resolve_scheme(directory: Path, name: str) -> ResolvedScheme:
    return resolve_table(directory, load_scheme(directory, name), None)


def _offering(resolved: ResolvedScheme) -> Offering:
    return Offering(
        name=resolved.scheme,
        dictionary=resolved.rules.dictionary,
        min_players=MIN_SEATS,
        max_players=seats_admitted(resolved.tiles, resolved.rules.rack_size),
    )
