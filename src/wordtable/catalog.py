from pathlib import Path

from wordcore.models.base import BaseFrozen
from wordtable.names import PresetName
from wordtable.paths import CONFIGURATION_SCHEMES_PATH
from wordtable.resolved import ResolvedScheme
from wordtable.rules import RulesConfig
from wordtable.scheme import SchemeConfig, SpecimenWord, load_scheme
from wordtable.settling import resolve_table


class Offering(BaseFrozen):
    name: PresetName
    specimen: SpecimenWord
    rules: RulesConfig


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
        specimen=resolved.specimen,
        rules=resolved.rules,
    )
